﻿
#include "pch.h"
#include <WS2tcpip.h>
#include "hooks.h"
#include "thread_pool.h"
#include "wechat_function.h"
#include "base64.h"
#include "rapidxml.hpp"
#include "http_client.h"

namespace offset = wxhelper::V3_9_5_81::offset;
namespace common = wxhelper::common;
namespace wxhelper {
    namespace hooks {

        static int kServerPort = 19099;
        static bool kMsgHookFlag = false;
        static char kServerIp[16] = "127.0.0.1";
        static bool kEnableHttp = false;
        static bool kLogHookFlag = false;

        static bool kSnsFinishHookFlag = false;

        struct mg_connection *connection = nullptr;
        static bool kMsgWsHookFlag = false;
        static bool kSnsFinishWsHookFlag = false;


        static UINT64 (*R_DoAddMsg)(UINT64, UINT64, UINT64) = (UINT64(*)(
                UINT64, UINT64, UINT64)) (Utils::GetWeChatWinBase() + offset::kDoAddMsg);

        static UINT64 (*R_Log)(UINT64, UINT64, UINT64, UINT64, UINT64, UINT64, UINT64,
                               UINT64, UINT64, UINT64, UINT64, UINT64) =
        (UINT64(*)(UINT64, UINT64, UINT64, UINT64, UINT64, UINT64, UINT64, UINT64,
                   UINT64, UINT64, UINT64,
                   UINT64)) (Utils::GetWeChatWinBase() + offset::kHookLog);

        static UINT64 (*R_OnSnsTimeLineSceneFinish)(UINT64, UINT64, UINT64) =
        (UINT64(*)(UINT64, UINT64, UINT64)) (Utils::GetWeChatWinBase() +
                                             offset::kOnSnsTimeLineSceneFinish);

        VOID CALLBACK SendMsgCallback(PTP_CALLBACK_INSTANCE instance, PVOID context,
                                      PTP_WORK Work) {
            common::InnerMessageStruct *msg = (common::InnerMessageStruct *) context;
            if (msg == NULL) {
                SPDLOG_INFO("add work:msg is null");
                return;
            }
            std::unique_ptr<common::InnerMessageStruct> sms(msg);
            nlohmann::json j_msg =
                    nlohmann::json::parse(msg->buffer, msg->buffer + msg->length, nullptr, false);
            if (j_msg.is_discarded() == true) {
                return;
            }
            std::string jstr = j_msg.dump() + "\n";

            if (kServerPort == 0) {
                SPDLOG_ERROR("http server port error :{}", kServerPort);
                return;
            }
            WSADATA was_data = {0};
            int ret = WSAStartup(MAKEWORD(2, 2), &was_data);
            if (ret != 0) {
                SPDLOG_ERROR("WSAStartup failed:{}", ret);
                return;
            }

            SOCKET client_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
            if (client_socket < 0) {
                SPDLOG_ERROR("socket init  fail");
                return;
            }
            BOOL status = false;
            sockaddr_in client_addr;
            memset(&client_addr, 0, sizeof(client_addr));
            client_addr.sin_family = AF_INET;
            client_addr.sin_port = htons((u_short) kServerPort);
            InetPtonA(AF_INET, kServerIp, &client_addr.sin_addr.s_addr);
            if (connect(client_socket, reinterpret_cast<sockaddr *>(&client_addr),
                        sizeof(sockaddr)) < 0) {
                SPDLOG_ERROR("socket connect  fail");
                goto clean;
            }
            char recv_buf[1024] = {0};
            ret = send(client_socket, jstr.c_str(), static_cast<int>(jstr.size()), 0);
            if (ret < 0) {
                SPDLOG_ERROR("socket send  fail ,ret:{}", ret);
                goto clean;
            }
            ret = shutdown(client_socket, SD_SEND);
            if (ret == SOCKET_ERROR) {
                SPDLOG_ERROR("shutdown failed with erro:{}", ret);
                goto clean;
            }
            ret = recv(client_socket, recv_buf, sizeof(recv_buf), 0);
            if (ret < 0) {
                SPDLOG_ERROR("socket recv  fail ,ret:{}", ret);
                goto clean;
            }
            clean:
            closesocket(client_socket);
            WSACleanup();
            return;
        }

        VOID CALLBACK SendHttpMsgCallback(PTP_CALLBACK_INSTANCE instance, PVOID context,
                                          PTP_WORK Work) {
            common::InnerMessageStruct *msg = (common::InnerMessageStruct *) context;
            if (msg == NULL) {
                SPDLOG_INFO("http msg is null");
                return;
            }

            std::unique_ptr<common::InnerMessageStruct> sms(msg);
            nlohmann::json j_msg =
                    nlohmann::json::parse(msg->buffer, msg->buffer + msg->length, nullptr, false);
            if (j_msg.is_discarded() == true) {
                return;
            }
            std::string jstr = j_msg.dump() + "\n";
            HttpClient::GetInstance().SendRequest(jstr);
        }

        void HandleSyncMsg(INT64 param1, INT64 param2, INT64 param3) {
            nlohmann::json msg;

            msg["pid"] = GetCurrentProcessId();
            msg["fromUser"] = Utils::ReadSKBuiltinString(*(INT64 *) (param2 + 0x18));
            msg["toUser"] = Utils::ReadSKBuiltinString(*(INT64 *) (param2 + 0x28));
            msg["content"] = Utils::ReadSKBuiltinString(*(INT64 *) (param2 + 0x30));
            msg["signature"] = Utils::ReadWeChatStr(*(INT64 *) (param2 + 0x48));
            msg["msgId"] = *(INT64 *) (param2 + 0x60);
            msg["msgSequence"] = *(DWORD *) (param2 + 0x5C);
            msg["createTime"] = *(DWORD *) (param2 + 0x58);
            msg["displayFullContent"] = Utils::ReadWeChatStr(*(INT64 *) (param2 + 0x50));
            DWORD type = *(DWORD *) (param2 + 0x24);
            msg["type"] = type;
            if (type == 3) {
                std::string img = Utils::ReadSKBuiltinBuffer(*(INT64 *) (param2 + 0x40));
                SPDLOG_INFO("encode size:{}", img.size());
                msg["base64Img"] = base64_encode(img);
            }
            std::string jstr = msg.dump() + '\n';
            common::InnerMessageStruct *inner_msg = new common::InnerMessageStruct;
            inner_msg->buffer = new char[jstr.size() + 1];
            memcpy(inner_msg->buffer, jstr.c_str(), jstr.size() + 1);
            inner_msg->length = jstr.size();
            if (kEnableHttp) {
                bool add = ThreadPool::GetInstance().AddWork(SendHttpMsgCallback, inner_msg);
                SPDLOG_INFO("add http msg work:{}", add);
            } else {
                bool add = ThreadPool::GetInstance().AddWork(SendMsgCallback, inner_msg);
                SPDLOG_INFO("add msg work:{}", add);
            }
            delete[] inner_msg->buffer;
            delete inner_msg;
            R_DoAddMsg(param1, param2, param3);
        }

        void HandleSNSMsg(INT64 param1, INT64 param2, INT64 param3) {
            nlohmann::json j_sns;
            INT64 begin_addr = *(INT64 *) (param2 + 0x30);
            INT64 end_addr = *(INT64 *) (param2 + 0x38);
            if (begin_addr == 0) {
                j_sns = {{"data", nlohmann::json::array()}};
            } else {
                while (begin_addr < end_addr) {
                    nlohmann::json j_item;
                    j_item["snsId"] = *(UINT64 *) (begin_addr);
                    j_item["createTime"] = *(DWORD *) (begin_addr + 0x38);
                    j_item["senderId"] = Utils::ReadWstringThenConvert(begin_addr + 0x18);
                    j_item["content"] = Utils::ReadWstringThenConvert(begin_addr + 0x48);
                    j_item["xml"] = Utils::ReadWstringThenConvert(begin_addr + 0x580);
                    j_sns["data"].push_back(j_item);
                    begin_addr += 0x11E0;
                }
            }
            std::string jstr = j_sns.dump() + '\n';
            common::InnerMessageStruct *inner_msg = new common::InnerMessageStruct;
            inner_msg->buffer = new char[jstr.size() + 1];
            memcpy(inner_msg->buffer, jstr.c_str(), jstr.size() + 1);
            inner_msg->length = jstr.size();
            if (kEnableHttp) {
                bool add = ThreadPool::GetInstance().AddWork(SendHttpMsgCallback, inner_msg);
                SPDLOG_INFO("hook sns add http msg work:{}", add);
            } else {
                bool add = ThreadPool::GetInstance().AddWork(SendMsgCallback, inner_msg);
                SPDLOG_INFO("hook sns add msg work:{}", add);
            }

            delete[] inner_msg->buffer;
            delete inner_msg;
            R_OnSnsTimeLineSceneFinish(param1, param2, param3);
        }

        int HookSyncMsg(std::string client_ip, int port, std::string url,
                        uint64_t timeout, bool enable) {
            if (kMsgHookFlag) {
                SPDLOG_INFO("recv msg hook already called");
                return 2;
            }
            kEnableHttp = enable;
            if (kEnableHttp) {
                HttpClient::GetInstance().SetConfig(url, timeout);
            }
            if (client_ip.size() < 1) {
                return -2;
            }

            kServerPort = port;
            strcpy_s(kServerIp, client_ip.c_str());
            UINT64 base = Utils::GetWeChatWinBase();
            if (!base) {
                SPDLOG_INFO("base addr is null");
                return -1;
            }

            // DetourRestoreAfterWith();
            DetourTransactionBegin();
            DetourUpdateThread(GetCurrentThread());
            DetourAttach(&(PVOID &) R_DoAddMsg, &HandleSyncMsg);
            LONG ret = DetourTransactionCommit();
            if (ret == NO_ERROR) {
                kMsgHookFlag = true;
            }
            SPDLOG_INFO("hook sync {}", ret);
            DetourTransactionBegin();
            DetourUpdateThread(GetCurrentThread());
            DetourAttach(&(PVOID &) R_OnSnsTimeLineSceneFinish, &HandleSNSMsg);
            ret = DetourTransactionCommit();
            if (ret == NO_ERROR) {
                kSnsFinishHookFlag = true;
            }
            SPDLOG_INFO("hook sns {}", ret);
            return ret;
        }

        int UnHookSyncMsg() {
            if (!kMsgHookFlag) {
                kMsgHookFlag = false;
                kEnableHttp = false;
                strcpy_s(kServerIp, "127.0.0.1");
                SPDLOG_INFO("hook sync msg reset");
                return NO_ERROR;
            }
            UINT64 base = Utils::GetWeChatWinBase();
            DetourTransactionBegin();
            DetourUpdateThread(GetCurrentThread());
            DetourDetach(&(PVOID &) R_DoAddMsg, &HandleSyncMsg);
            LONG ret = DetourTransactionCommit();
            if (ret == NO_ERROR) {
                kMsgHookFlag = false;
                kEnableHttp = false;
                strcpy_s(kServerIp, "127.0.0.1");
            }
            return ret;
        }

        void HandleWsSyncMsg(INT64 param1, INT64 param2, INT64 param3) {
            nlohmann::json msg;
            std::string ctnt;

            msg["pid"] = GetCurrentProcessId();
            msg["fromUser"] = Utils::ReadSKBuiltinString(*(INT64 *) (param2 + 0x18));
            msg["toUser"] = Utils::ReadSKBuiltinString(*(INT64 *) (param2 + 0x28));
            ctnt = Utils::ReadSKBuiltinString(*(INT64 *) (param2 + 0x30));
            msg["content"] = ctnt;
            msg["signature"] = Utils::ReadWeChatStr(*(INT64 *) (param2 + 0x48));
            msg["msgId"] = *(INT64 *) (param2 + 0x60);
            msg["msgSequence"] = *(DWORD *) (param2 + 0x5C);
            msg["createTime"] = *(DWORD *) (param2 + 0x58);
            msg["displayFullContent"] = Utils::ReadWeChatStr(*(INT64 *) (param2 + 0x50));
            DWORD type = *(DWORD *) (param2 + 0x24);
            msg["type"] = type;

            if (type == 3) {
                std::string img = Utils::ReadSKBuiltinBuffer(*(INT64 *) (param2 + 0x40));
                SPDLOG_INFO("encode size:{}", img.size());
                msg["base64Img"] = base64_encode(img);
            } else if (type == 51 && ctnt.compare(0, 12, "<msg>\n<op id") == 0) {
                std::string num;
                for (int i = 14; i < 16; i++) {
                    if (isdigit(ctnt[i])) {
                        num.push_back(ctnt[i]);
                    }
                }
                msg["type"] = std::stoi(num) + 10002;
            } else if (type == 49) {
                int start = (int) ctnt.find('<');
                rapidxml::xml_document<> doc;
                doc.parse<0>(const_cast<char *>(ctnt.c_str() + start));  // RapidXML doesn't allow const char* in parse()
                rapidxml::xml_node<> *msgNode = doc.first_node("msg");
                rapidxml::xml_node<> *appmsgNode = msgNode->first_node("appmsg");

                const char *title = appmsgNode->first_node("type")->value();
                if (title != nullptr) {
                    int trans = std::stoi(title);
                    switch (trans) {
                        case 3:
                            msg["type"] = 53;
                            break;
                        case 51:
                            msg["type"] = 52;
                            break;
                        default:
                            msg["type"] = trans;
                            break;
                    }
                }
            }
            std::string jstr = msg.dump();
            mg_ws_send(connection, jstr.c_str(), jstr.length(), WEBSOCKET_OP_TEXT);
            R_DoAddMsg(param1, param2, param3);
        }

        void HandleWsSNSMsg(INT64 param1, INT64 param2, INT64 param3) {
            nlohmann::json j_sns;
            INT64 begin_addr = *(INT64 *) (param2 + 0x30);
            INT64 end_addr = *(INT64 *) (param2 + 0x38);
            if (begin_addr == 0) {
                j_sns = {{"data", nlohmann::json::array()}};
            } else {
                while (begin_addr < end_addr) {
                    nlohmann::json j_item;
                    j_item["snsId"] = *(UINT64 *) (begin_addr);
                    j_item["createTime"] = *(DWORD *) (begin_addr + 0x38);
                    j_item["senderId"] = Utils::ReadWstringThenConvert(begin_addr + 0x18);
                    j_item["content"] = Utils::ReadWstringThenConvert(begin_addr + 0x48);
                    j_item["xml"] = Utils::ReadWstringThenConvert(begin_addr + 0x580);
                    j_sns["data"].push_back(j_item);
                    begin_addr += 0x11E0;
                }
            }
            j_sns["type"] = common::RECV_HOOK_SNS;
            std::string jstr = j_sns.dump();
            mg_ws_send(connection, jstr.c_str(), jstr.length(), WEBSOCKET_OP_TEXT);
            R_OnSnsTimeLineSceneFinish(param1, param2, param3);
        }

        int HookWsSyncMsg(struct mg_connection *c) {
            nlohmann::json res = {{"code", 200},
                                  {"msg",  "WebSocket server is started"},
                                  {"type", common::RECV_SERVER_HINT},
                                  {"data", "This message is from WxInject server"}};
            std::string jstr = res.dump();
            mg_ws_send(c, jstr.c_str(), jstr.length(), WEBSOCKET_OP_TEXT);
            if (kMsgWsHookFlag) {
                SPDLOG_INFO("hook sync msg websocket has started");
                return NO_ERROR;
            }
            // DetourRestoreAfterWith();
            connection = c;
            DetourTransactionBegin();
            DetourUpdateThread(GetCurrentThread());
            DetourAttach(&(PVOID &) R_DoAddMsg, &HandleWsSyncMsg);
            LONG ret = DetourTransactionCommit();
            if (ret == NO_ERROR) {
                kMsgWsHookFlag = true;
            } else {
                SPDLOG_INFO("hook sns error {}", ret);
            }

            if (kSnsFinishWsHookFlag) {
                SPDLOG_INFO("hook sync sns_msg websocket has started");
                return NO_ERROR;
            }
            DetourTransactionBegin();
            DetourUpdateThread(GetCurrentThread());
            DetourAttach(&(PVOID &) R_OnSnsTimeLineSceneFinish, &HandleWsSNSMsg);
            ret = DetourTransactionCommit();
            if (ret == NO_ERROR) {
                kSnsFinishWsHookFlag = true;
            } else {
                SPDLOG_INFO("hook sns error {}", ret);
            }
            return ret;
        }

        int UnHookWsSyncMsg() {
            if (!kMsgWsHookFlag) {
                kMsgWsHookFlag = false;
                SPDLOG_INFO("hook sync msg not started yet");
                return NO_ERROR;
            }
            DetourTransactionBegin();
            DetourUpdateThread(GetCurrentThread());
            DetourDetach(&(PVOID &) R_DoAddMsg, &HandleWsSyncMsg);
            LONG ret = DetourTransactionCommit();
            if (ret == NO_ERROR) {
                kMsgWsHookFlag = false;
            }
            if (!kSnsFinishWsHookFlag) {
                kSnsFinishWsHookFlag = false;
                SPDLOG_INFO("hook sync sns_msg not started yet");
                return NO_ERROR;
            }
            DetourTransactionBegin();
            DetourUpdateThread(GetCurrentThread());
            DetourDetach(&(PVOID &) R_OnSnsTimeLineSceneFinish, &HandleWsSNSMsg);
            ret = DetourTransactionCommit();
            if (ret == NO_ERROR) {
                kSnsFinishWsHookFlag = false;
            }
            if (!kMsgWsHookFlag && !kSnsFinishWsHookFlag) {
                connection = nullptr;
            }
            return ret;
        }

        UINT64 HandlePrintLog(UINT64 param1, UINT64 param2, UINT64 param3, UINT64 param4,
                              UINT64 param5, UINT64 param6, UINT64 param7, UINT64 param8,
                              UINT64 param9, UINT64 param10, UINT64 param11,
                              UINT64 param12) {
            UINT64 p = R_Log(param1, param2, param3, param4, param5, param6, param7, param8, param9,
                             param10, param11, param12);
            if (p == 0 || p == 1) {
                return p;
            }
            char *msg = (char *) p;
            if (msg != NULL) {
                // INT64 size = *(INT64 *)(p - 0x8);
                std::string str(msg);
                std::wstring ws = Utils::UTF8ToWstring(str);
                std::string out = Utils::WstringToAnsi(ws, CP_ACP);
                spdlog::info("Wechat log:{}", out);
            }
            return p;
        }

        int HookLog() {
            if (kLogHookFlag) {
                SPDLOG_INFO("log hook already called");
                return 2;
            }

            UINT64 base = Utils::GetWeChatWinBase();
            if (!base) {
                SPDLOG_INFO("base addr is null");
                return -1;
            }

            // DetourRestoreAfterWith();
            DetourTransactionBegin();
            DetourUpdateThread(GetCurrentThread());
            UINT64 do_add_msg_addr = base + offset::kHookLog;
            DetourAttach(&(PVOID &) R_Log, &HandlePrintLog);
            LONG ret = DetourTransactionCommit();
            if (ret == NO_ERROR) {
                kLogHookFlag = true;
            }
            return ret;
        }

        int UnHookLog() {
            if (!kLogHookFlag) {
                kLogHookFlag = false;
                SPDLOG_INFO("hook log reset");
                return NO_ERROR;
            }
            UINT64 base = Utils::GetWeChatWinBase();
            DetourTransactionBegin();
            DetourUpdateThread(GetCurrentThread());
            UINT64 do_add_msg_addr = base + offset::kHookLog;
            DetourDetach(&(PVOID &) R_Log, &HandlePrintLog);
            LONG ret = DetourTransactionCommit();
            if (ret == NO_ERROR) {
                kLogHookFlag = false;
            }
            return ret;
        }

    }  // namespace hooks
}  // namespace wxhelper