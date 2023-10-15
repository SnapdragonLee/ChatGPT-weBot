#include "pch.h"
#include "http_server_callback.h"
#include "http_server.h"
#include "export.h"
#include "global_context.h"
#include "hooks.h"
#include "db.h"


#define STR2ULL(str) (wxhelper::Utils::IsDigit(str) ? stoull(str) : 0)
#define STR2LL(str) (wxhelper::Utils::IsDigit(str) ? stoll(str) : 0)
#define STR2I(str) (wxhelper::Utils::IsDigit(str) ? stoi(str) : 0)
namespace common = wxhelper::common;

int GetIntParam(nlohmann::json data, std::string key) {
    int result;
    try {
        result = data[key].get<int>();
    } catch (nlohmann::json::exception) {
        result = STR2I(data[key].get<std::string>());
    }
    return result;
}

INT64 GetINT64Param(nlohmann::json data, std::string key) {
    INT64 result;
    try {
        result = data[key].get<INT64>();
    } catch (nlohmann::json::exception) {
        result = STR2LL(data[key].get<std::string>());
    }
    return result;
}

INT64 GetUINT64Param(nlohmann::json data, std::string key) {
    UINT64 result;
    try {
        result = data[key].get<UINT64>();
    } catch (nlohmann::json::exception) {
        result = STR2ULL(data[key].get<std::string>());
    }
    return result;
}

std::string GetStringParam(nlohmann::json data, std::string key) {
    return data[key].get<std::string>();
}

std::wstring GetWStringParam(nlohmann::json data, std::string key) {
    return wxhelper::Utils::UTF8ToWstring(data[key].get<std::string>());
}

std::vector<std::wstring> GetArrayParam(nlohmann::json data, std::string key) {
    std::vector<std::wstring> result;
    std::wstring param = GetWStringParam(data, key);
    result = wxhelper::Utils::split(param, L',');
    return result;
}


void StartHttpServer(wxhelper::HttpServer *server) {
    int port = server->GetPort();
    std::string lsten_addr = "http://0.0.0.0:" + std::to_string(port);
    if (mg_http_listen(const_cast<mg_mgr *>(server->GetMgr()), lsten_addr.c_str(),
                       EventHandler,
                       const_cast<mg_mgr *>(server->GetMgr())) == NULL) {
        SPDLOG_INFO("http server  listen fail.port:{}", port);
#ifdef _DEBUG
        MG_INFO(("http server  listen fail.port: %d", port));
#endif
        return;
    }
    for (;;) {
        mg_mgr_poll(const_cast<mg_mgr *>(server->GetMgr()), 1000);
    }
}

void EventHandler(struct mg_connection *c, int ev, void *ev_data,
                  void *fn_data) {
    if (ev == MG_EV_OPEN) {
    } else if (ev == MG_EV_HTTP_MSG) {
        struct mg_http_message *hm = (struct mg_http_message *) ev_data;
        if (mg_http_match_uri(hm, "/ws")) {
            mg_ws_upgrade(c, hm, NULL);
        } else if (mg_http_match_uri(hm, "/api/*")) {
            HandleHttpRequest(c, hm);
        } else {
            nlohmann::json res = {{"code", 400},
                                  {"msg",  "invalid url, please check url"},
                                  {"data", NULL}};
            std::string ret = res.dump();
            mg_http_reply(c, 200, "Content-Type: application/json\r\n", "%s\n",
                          ret.c_str());
        }
    } else if (ev == MG_EV_WS_OPEN) {
        wxhelper::hooks::HookWsSyncMsg(c);
    } else if (ev == MG_EV_WS_MSG) {
        HandleWebsocketRequest(c, ev_data);
    } else if (ev == MG_EV_CLOSE) {
        wxhelper::hooks::UnHookWsSyncMsg();
    }
    (void) fn_data;
}

void HandleHttpRequest(struct mg_connection *c, void *ev_data) {
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;
    std::string ret = R"({"code":200,"msg":"success"})";
    try {
        ret = HttpDispatch(c, hm);
    } catch (nlohmann::json::exception &e) {
        nlohmann::json res = {{"code", "500"},
                              {"msg",  e.what()},
                              {"data", NULL}};
        ret = res.dump();
    }
    if (ret != "") {
        mg_http_reply(c, 200, "Content-Type: application/json\r\n", "%s\n",
                      ret.c_str());
    }
}

std::string HttpDispatch(struct mg_connection *c, struct mg_http_message *hm) {
    std::string ret;
    if (mg_vcasecmp(&hm->method, "GET") == 0) {
        nlohmann::json ret_data = {{"code", 200},
                                   {"data", {}},
                                   {"msg",  "not support get method,use post."}};
        ret = ret_data.dump();
        return ret;
    }

    nlohmann::json j_param = nlohmann::json::parse(
            hm->body.ptr, hm->body.ptr + hm->body.len, nullptr, false);
    if (hm->body.len != 0 && j_param.is_discarded() == true) {
        nlohmann::json ret_data = {
                {"code", 200},
                {"data", {}},
                {"msg",  "json string is invalid."}};
        ret = ret_data.dump();
        return ret;
    }
    if (wxhelper::GlobalContext::GetInstance().state !=
        wxhelper::GlobalContextState::INITIALIZED) {
        nlohmann::json ret_data = {
                {"code", 200},
                {"data", {}},
                {"msg",  "global context is initializing"}};
        ret = ret_data.dump();
        return ret;
    }
    if (mg_http_match_uri(hm, "/api/checkLogin")) {
        INT64 success = wxhelper::GlobalContext::GetInstance().mgr->CheckLogin();
        nlohmann::json ret_data = {
                {"code", success},
                {"data", {}},
                {"msg",  "success"}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/userInfo")) {
        common::SelfInfoInner self_info;
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->GetSelfInfo(self_info);
        nlohmann::json ret_data = {
                {"code", success},
                {"data", {}},
                {"msg",  "success"}};
        if (success) {
            nlohmann::json j_info = {
                    {"name",            self_info.name},
                    {"city",            self_info.city},
                    {"province",        self_info.province},
                    {"country",         self_info.country},
                    {"account",         self_info.account},
                    {"wxid",            self_info.wxid},
                    {"mobile",          self_info.mobile},
                    {"headImage",       self_info.head_img},
                    {"signature",       self_info.signature},
                    {"dataSavePath",    self_info.data_save_path},
                    {"currentDataPath", self_info.current_data_path},
                    {"dbKey",           self_info.db_key},
            };
            ret_data["data"] = j_info;
        }
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/sendTextMsg")) {
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        std::wstring msg = GetWStringParam(j_param, "msg");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->SendTextMsg(wxid, msg);
        nlohmann::json ret_data = {
                {"code", success},
                {"data", {}},
                {"msg",  "success"}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/hookSyncMsg")) {
        int port = GetIntParam(j_param, "port");
        std::string ip = GetStringParam(j_param, "ip");
        int enable = GetIntParam(j_param, "enableHttp");
        std::string url = "";
        int timeout = 0;
        if (enable) {
            url = GetStringParam(j_param, "url");
            timeout = GetIntParam(j_param, "timeout");
        }
        INT64 success =
                wxhelper::hooks::HookSyncMsg(ip, port, url, timeout, enable);
        nlohmann::json ret_data = {
                {"code", success},
                {"data", {}},
                {"msg",  "success"}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/sendImagesMsg")) {
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        std::wstring path = GetWStringParam(j_param, "imagePath");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->SendImageMsg(wxid, path);
        nlohmann::json ret_data = {
                {"code", success},
                {"data", {}},
                {"msg",  "success"}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/sendFileMsg")) {
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        std::wstring path = GetWStringParam(j_param, "filePath");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->SendFileMsg(wxid, path);
        nlohmann::json ret_data = {
                {"code", success},
                {"data", {}},
                {"msg",  "success"}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/getContactList")) {
        std::vector<common::ContactInner> vec;
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->GetContacts(vec);
        nlohmann::json ret_data = {
                {"code", success},
                {"data", {}},
                {"msg",  "success"}};
        for (unsigned int i = 0; i < vec.size(); i++) {
            nlohmann::json item = {
                    {"customAccount", vec[i].custom_account},
                    {"encryptName",   vec[i].encrypt_name},
                    {"type",          vec[i].type},
                    {"verifyFlag",    vec[i].verify_flag},
                    {"wxid",          vec[i].wxid},
                    {"nickname",      vec[i].nickname},
                    {"pinyin",        vec[i].pinyin},
                    {"pinyinAll",     vec[i].pinyin_all},
                    {"reserved1",     vec[i].reserved1},
                    {"reserved2",     vec[i].reserved2},
            };
            ret_data["data"].push_back(item);
        }
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/unhookSyncMsg")) {
        INT64 success = wxhelper::hooks::UnHookSyncMsg();
        nlohmann::json ret_data = {
                {"code", success},
                {"data", {}},
                {"msg",  "success"}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/getDBInfo")) {
        std::vector<void *> v_ptr = wxhelper::DB::GetInstance().GetDbHandles();
        nlohmann::json ret_data = {{"data", nlohmann::json::array()}};
        for (unsigned int i = 0; i < v_ptr.size(); i++) {
            nlohmann::json db_info;
            db_info["tables"] = nlohmann::json::array();
            common::DatabaseInfo *db =
                    reinterpret_cast<common::DatabaseInfo *>(v_ptr[i]);
            db_info["handle"] = db->handle;
            std::wstring dbname(db->db_name);
            db_info["databaseName"] = wxhelper::Utils::WstringToUTF8(dbname);
            for (auto table: db->tables) {
                nlohmann::json table_info = {{"name",      table.name},
                                             {"tableName", table.table_name},
                                             {"sql",       table.sql},
                                             {"rootpage",  table.rootpage}};
                db_info["tables"].push_back(table_info);
            }
            ret_data["data"].push_back(db_info);
        }
        ret_data["code"] = 1;
        ret_data["msg"] = "success";
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/execSql")) {
        UINT64 db_handle = GetINT64Param(j_param, "dbHandle");
        std::string sql = GetStringParam(j_param, "sql");
        std::vector<std::vector<std::string>> items;
        int success =
                wxhelper::DB::GetInstance().Select(db_handle, sql.c_str(), items);
        nlohmann::json ret_data = {{"data", nlohmann::json::array()},
                                   {"code", success},
                                   {"msg",  "success"}};
        if (success == 0) {
            ret_data["msg"] = "no data";
            ret = ret_data.dump();
            return ret;
        }
        for (auto it: items) {
            nlohmann::json temp_arr = nlohmann::json::array();
            for (size_t i = 0; i < it.size(); i++) {
                temp_arr.push_back(it[i]);
            }
            ret_data["data"].push_back(temp_arr);
        }
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/getChatRoomDetailInfo")) {
        std::wstring chat_room_id = GetWStringParam(j_param, "chatRoomId");
        common::ChatRoomInfoInner chat_room_detail;
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->GetChatRoomDetailInfo(
                        chat_room_id, chat_room_detail);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};

        nlohmann::json detail = {
                {"chatRoomId", chat_room_detail.chat_room_id},
                {"notice",     chat_room_detail.notice},
                {"admin",      chat_room_detail.admin},
                {"xml",        chat_room_detail.xml},
        };
        ret_data["data"] = detail;
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/addMemberToChatRoom")) {
        std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
        std::vector<std::wstring> wxids = GetArrayParam(j_param, "memberIds");
        std::vector<std::wstring> wxid_list;
        for (unsigned int i = 0; i < wxids.size(); i++) {
            wxid_list.push_back(wxids[i]);
        }
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->AddMemberToChatRoom(
                        room_id, wxid_list);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/modifyNickname")) {
        std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        std::wstring nickName = GetWStringParam(j_param, "nickName");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->ModChatRoomMemberNickName(
                        room_id, wxid, nickName);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/delMemberFromChatRoom")) {
        std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
        std::vector<std::wstring> wxids = GetArrayParam(j_param, "memberIds");
        std::vector<std::wstring> wxid_list;
        for (unsigned int i = 0; i < wxids.size(); i++) {
            wxid_list.push_back(wxids[i]);
        }
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->DelMemberFromChatRoom(
                        room_id, wxid_list);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/getMemberFromChatRoom")) {
        std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
        common::ChatRoomMemberInner member;
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->GetMemberFromChatRoom(
                        room_id, member);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        if (success >= 0) {
            nlohmann::json member_info = {
                    {"admin",          member.admin},
                    {"chatRoomId",     member.chat_room_id},
                    {"members",        member.member},
                    {"adminNickname",  member.admin_nickname},
                    {"memberNickname", member.member_nickname},
            };
            ret_data["data"] = member_info;
        }
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/topMsg")) {
        INT64 msg_id = GetINT64Param(j_param, "msgId");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->SetTopMsg(msg_id);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/removeTopMsg")) {
        std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
        INT64 msg_id = GetINT64Param(j_param, "msgId");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->RemoveTopMsg(room_id, msg_id);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/InviteMemberToChatRoom")) {
        std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
        std::vector<std::wstring> wxids = GetArrayParam(j_param, "memberIds");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->InviteMemberToChatRoom(
                        room_id, wxids);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/hookLog")) {
        int success = wxhelper::hooks::HookLog();
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/unhookLog")) {
        int success = wxhelper::hooks::UnHookLog();
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/createChatRoom")) {
        std::vector<std::wstring> wxids = GetArrayParam(j_param, "memberIds");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->CreateChatRoom(wxids);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/quitChatRoom")) {
        std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->QuitChatRoom(room_id);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/forwardMsg")) {
        INT64 msg_id = GetINT64Param(j_param, "msgId");
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->ForwardMsg(msg_id, wxid);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/getSNSFirstPage")) {
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->GetSNSFirstPage();
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/getSNSNextPage")) {
        UINT64 snsid = GetUINT64Param(j_param, "snsId");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->GetSNSNextPage(snsid);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/addFavFromMsg")) {
        UINT64 msg_id = GetUINT64Param(j_param, "msgId");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->AddFavFromMsg(msg_id);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/addFavFromImage")) {
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        std::wstring image_path = GetWStringParam(j_param, "imagePath");
        INT64 success = wxhelper::GlobalContext::GetInstance().mgr->AddFavFromImage(
                wxid, image_path);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/sendAtText")) {
        std::wstring chat_room_id = GetWStringParam(j_param, "chatRoomId");
        std::vector<std::wstring> wxids = GetArrayParam(j_param, "wxids");
        std::wstring msg = GetWStringParam(j_param, "msg");
        std::vector<std::wstring> wxid_list;
        for (unsigned int i = 0; i < wxids.size(); i++) {
            wxid_list.push_back(wxids[i]);
        }
        INT64 success = wxhelper::GlobalContext::GetInstance().mgr->SendAtText(
                chat_room_id, wxid_list, msg);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/getContactProfile")) {
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        common::ContactProfileInner profile;
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->GetContactByWxid(wxid,
                                                                             profile);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        if (success == 1) {
            nlohmann::json contact_profile = {
                    {"account",   profile.account},
                    {"headImage", profile.head_image},
                    {"nickname",  profile.nickname},
                    {"v3",        profile.v3},
                    {"wxid",      profile.wxid},
            };
            ret_data["data"] = contact_profile;
        }
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/downloadAttach")) {
        UINT64 msg_id = GetUINT64Param(j_param, "msgId");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->DoDownloadTask(msg_id);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/forwardPublicMsg")) {
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        std::wstring appname = GetWStringParam(j_param, "appName");
        std::wstring username = GetWStringParam(j_param, "userName");
        std::wstring title = GetWStringParam(j_param, "title");
        std::wstring url = GetWStringParam(j_param, "url");
        std::wstring thumburl = GetWStringParam(j_param, "thumbUrl");
        std::wstring digest = GetWStringParam(j_param, "digest");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->ForwardPublicMsg(
                        wxid, title, url, thumburl, username, appname, digest);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/forwardPublicMsgByMsgId")) {
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        UINT64 msg_id = GetUINT64Param(j_param, "msgId");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->ForwardPublicMsgByMsgId(
                        wxid, msg_id);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/decodeImage")) {
        std::wstring file_path = GetWStringParam(j_param, "filePath");
        std::wstring store_dir = GetWStringParam(j_param, "storeDir");
        INT64 success = wxhelper::GlobalContext::GetInstance().mgr->DecodeImage(
                file_path, store_dir);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/getVoiceByMsgId")) {
        UINT64 msg_id = GetUINT64Param(j_param, "msgId");
        std::wstring store_dir = GetWStringParam(j_param, "storeDir");
        INT64 success = wxhelper::GlobalContext::GetInstance().mgr->GetVoiceByDB(
                msg_id, store_dir);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/sendCustomEmotion")) {
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        std::wstring file_path = GetWStringParam(j_param, "filePath");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->SendCustomEmotion(file_path,
                                                                              wxid);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/sendApplet")) {
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        std::wstring waid_concat = GetWStringParam(j_param, "waidConcat");
        std::string waid = GetStringParam(j_param, "waid");
        std::string app_wxid = GetStringParam(j_param, "appletWxid");
        std::string json_param = GetStringParam(j_param, "jsonParam");
        std::string head_url = GetStringParam(j_param, "headImgUrl");
        std::string main_img = GetStringParam(j_param, "mainImg");
        std::string index_page = GetStringParam(j_param, "indexPage");

        std::wstring waid_w = wxhelper::Utils::UTF8ToWstring(waid);

        INT64 success = wxhelper::GlobalContext::GetInstance().mgr->SendApplet(
                wxid, waid_concat, waid_w, waid, app_wxid, json_param, head_url,
                main_img, index_page);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/sendPatMsg")) {
        std::wstring room_id = GetWStringParam(j_param, "receiver");
        std::wstring wxid = GetWStringParam(j_param, "wxid");
        INT64 success =
                wxhelper::GlobalContext::GetInstance().mgr->SendPatMsg(room_id, wxid);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/ocr")) {
        std::wstring image_path = GetWStringParam(j_param, "imagePath");
        std::string text("");
        INT64 success = wxhelper::GlobalContext::GetInstance().mgr->DoOCRTask(image_path, text);
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", text}};
        ret = ret_data.dump();
        return ret;
    } else if (mg_http_match_uri(hm, "/api/test")) {
        INT64 success = wxhelper::GlobalContext::GetInstance().mgr->Test();
        nlohmann::json ret_data = {
                {"code", success},
                {"msg",  "success"},
                {"data", {}}};
        ret = ret_data.dump();
        return ret;
    } else {
        nlohmann::json ret_data = {
                {"code", 200},
                {"data", {}},
                {"msg",  "not support url"}};
        ret = ret_data.dump();
        return ret;
    }
}

void HandleWebsocketRequest(struct mg_connection *c, void *ev_data) {
    struct mg_ws_message *wm = (struct mg_ws_message *) ev_data;
    std::string ret;
    try {
        WsDispatch(wm, ret);
    } catch (nlohmann::json::exception &e) {
        nlohmann::json res = {{"code", "500"},
                              {"msg",  e.what()},
                              {"data", NULL}};
        ret = res.dump();
    }
    if (!ret.empty()) {
        mg_ws_send(c, ret.c_str(), ret.length(), WEBSOCKET_OP_TEXT);
    }
}

void WsDispatch(struct mg_ws_message *wm, std::string &output) {
    nlohmann::json j_param = nlohmann::json::parse(
            wm->data.ptr, wm->data.ptr + wm->data.len, nullptr, false);
    nlohmann::json ret_data;

    if (wm->data.len != 0 && j_param.is_discarded()) {
        ret_data = {
                {"code", 200},
                {"data", {}},
                {"type", common::RECV_SERVER_HINT},
                {"msg",  "json string is invalid."}};
        output = ret_data.dump();
        return;
    }
    if (wxhelper::GlobalContext::GetInstance().state !=
        wxhelper::GlobalContextState::INITIALIZED) {
        ret_data = {
                {"code", 200},
                {"data", {}},
                {"type", common::RECV_SERVER_HINT},
                {"msg",  "global context is initializing"}};
        output = ret_data.dump();
        return;
    }

    INT64 success = 0;
    int type = GetIntParam(j_param, "type");

    switch (type) {
        case common::CHECK_LOGIN: {
            success = wxhelper::GlobalContext::GetInstance().mgr->CheckLogin();
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::CHECK_SELF_INFO: {
            common::SelfInfoInner self_info;
            success = wxhelper::GlobalContext::GetInstance().mgr->GetSelfInfo(self_info);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            if (success) {
                nlohmann::json j_info = {
                        {"name",            self_info.name},
                        {"city",            self_info.city},
                        {"province",        self_info.province},
                        {"country",         self_info.country},
                        {"account",         self_info.account},
                        {"wxid",            self_info.wxid},
                        {"mobile",          self_info.mobile},
                        {"headImage",       self_info.head_img},
                        {"signature",       self_info.signature},
                        {"dataSavePath",    self_info.data_save_path},
                        {"currentDataPath", self_info.current_data_path},
                        {"dbKey",           self_info.db_key},
                };
                ret_data["data"] = j_info;
            }
            output = ret_data.dump();
            break;
        }

        case common::SEND_TXT_MSG: {
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            std::wstring msg = GetWStringParam(j_param, "msg");
            success = wxhelper::GlobalContext::GetInstance().mgr->SendTextMsg(wxid, msg);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::SEND_TXT_AT_MSG: {
            std::wstring chat_room_id = GetWStringParam(j_param, "chatRoomId");
            std::vector<std::wstring> wxids = GetArrayParam(j_param, "wxids");
            std::wstring msg = GetWStringParam(j_param, "msg");
            std::vector<std::wstring> wxid_list;
            for (const auto &wxid: wxids) {
                wxid_list.push_back(wxid);
            }
            success = wxhelper::GlobalContext::GetInstance().mgr->SendAtText(
                    chat_room_id, wxid_list, msg);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::SEND_PIC_MSG: {
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            std::wstring path = GetWStringParam(j_param, "imagePath");
            success = wxhelper::GlobalContext::GetInstance().mgr->SendImageMsg(wxid, path);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::SEND_ATTACH_FILE: {
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            std::wstring path = GetWStringParam(j_param, "filePath");
            success = wxhelper::GlobalContext::GetInstance().mgr->SendFileMsg(wxid, path);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::GET_USER_LIST: {
            std::vector<common::ContactInner> vec;
            success = wxhelper::GlobalContext::GetInstance().mgr->GetContacts(vec);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            for (unsigned int i = 0; i < vec.size(); i++) {
                nlohmann::json item = {
                        {"customAccount", vec[i].custom_account},
                        {"encryptName",   vec[i].encrypt_name},
                        {"type",          vec[i].type},
                        {"verifyFlag",    vec[i].verify_flag},
                        {"wxid",          vec[i].wxid},
                        {"nickname",      vec[i].nickname},
                        {"pinyin",        vec[i].pinyin},
                        {"pinyinAll",     vec[i].pinyin_all},
                        {"reserved1",     vec[i].reserved1},
                        {"reserved2",     vec[i].reserved2},
                };
                ret_data["data"].push_back(item);
            }
            output = ret_data.dump();
            break;
        }

        case common::CHECK_DB_INFO: {
            std::vector<void *> v_ptr = wxhelper::DB::GetInstance().GetDbHandles();
            ret_data = {{"data", nlohmann::json::array()}};
            for (unsigned int i = 0; i < v_ptr.size(); i++) {
                nlohmann::json db_info;
                db_info["tables"] = nlohmann::json::array();
                common::DatabaseInfo *db =
                        reinterpret_cast<common::DatabaseInfo *>(v_ptr[i]);
                db_info["handle"] = db->handle;
                std::wstring dbname(db->db_name);
                db_info["databaseName"] = wxhelper::Utils::WstringToUTF8(dbname);
                for (auto table: db->tables) {
                    nlohmann::json table_info = {{"name",      table.name},
                                                 {"tableName", table.table_name},
                                                 {"sql",       table.sql},
                                                 {"rootpage",  table.rootpage}};
                    db_info["tables"].push_back(table_info);
                }
                ret_data["data"].push_back(db_info);
            }
            ret_data["code"] = 1;
            ret_data["type"] = type;
            ret_data["msg"] = "success";
            output = ret_data.dump();
            break;
        }

        case common::EXEC_SQL: {
            UINT64 db_handle = GetINT64Param(j_param, "dbHandle");
            std::string sql = GetStringParam(j_param, "sql");
            std::vector<std::vector<std::string>> items;
            success = wxhelper::DB::GetInstance().Select(db_handle, sql.c_str(), items);
            ret_data = {{"code", success},
                        {"data", nlohmann::json::array()},
                        {"type", type},
                        {"msg",  "success"}};
            if (success == 0) {
                ret_data["msg"] = "no data";
                output = ret_data.dump();
                break;
            }
            for (auto it: items) {
                nlohmann::json temp_arr = nlohmann::json::array();
                for (size_t i = 0; i < it.size(); i++) {
                    temp_arr.push_back(it[i]);
                }
                ret_data["data"].push_back(temp_arr);
            }
            output = ret_data.dump();
            break;
        }

        case common::GET_CHATROOM_INFO: {
            std::wstring chat_room_id = GetWStringParam(j_param, "chatRoomId");
            common::ChatRoomInfoInner chat_room_detail;
            success = wxhelper::GlobalContext::GetInstance().mgr->GetChatRoomDetailInfo(
                    chat_room_id, chat_room_detail);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};

            nlohmann::json detail = {
                    {"chatRoomId", chat_room_detail.chat_room_id},
                    {"notice",     chat_room_detail.notice},
                    {"admin",      chat_room_detail.admin},
                    {"xml",        chat_room_detail.xml},
            };
            ret_data["data"] = detail;
            output = ret_data.dump();
            break;
        }

        case common::ADD_MEMBER_CHATROOM: {
            std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
            std::vector<std::wstring> wxids = GetArrayParam(j_param, "memberIds");
            std::vector<std::wstring> wxid_list;
            for (unsigned int i = 0; i < wxids.size(); i++) {
                wxid_list.push_back(wxids[i]);
            }
            success = wxhelper::GlobalContext::GetInstance().mgr->AddMemberToChatRoom(
                    room_id, wxid_list);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::MODIFY_SELF_NAME: {
            std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            std::wstring nickName = GetWStringParam(j_param, "nickName");
            success = wxhelper::GlobalContext::GetInstance().mgr->ModChatRoomMemberNickName(
                    room_id, wxid, nickName);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::DEL_MEMBER_CHATROOM: {
            std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
            std::vector<std::wstring> wxids = GetArrayParam(j_param, "memberIds");
            std::vector<std::wstring> wxid_list;
            for (unsigned int i = 0; i < wxids.size(); i++) {
                wxid_list.push_back(wxids[i]);
            }
            success = wxhelper::GlobalContext::GetInstance().mgr->DelMemberFromChatRoom(
                    room_id, wxid_list);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::GET_CHATROOM_MEMBER: {
            std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
            common::ChatRoomMemberInner member;
            success = wxhelper::GlobalContext::GetInstance().mgr->GetMemberFromChatRoom(
                    room_id, member);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            if (success >= 0) {
                nlohmann::json member_info = {
                        {"admin",          member.admin},
                        {"chatRoomId",     member.chat_room_id},
                        {"members",        member.member},
                        {"adminNickname",  member.admin_nickname},
                        {"memberNickname", member.member_nickname},
                };
                ret_data["data"] = member_info;
            }
            output = ret_data.dump();
            break;
        }

        case common::ADD_TOP_MSG: {
            INT64 msg_id = GetINT64Param(j_param, "msgId");
            success = wxhelper::GlobalContext::GetInstance().mgr->SetTopMsg(msg_id);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::DEL_TOP_MSG: {
            std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
            INT64 msg_id = GetINT64Param(j_param, "msgId");
            success = wxhelper::GlobalContext::GetInstance().mgr->RemoveTopMsg(room_id, msg_id);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::INVITE_MEMBER_CHATROOM: {
            std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
            std::vector<std::wstring> wxids = GetArrayParam(j_param, "memberIds");
            success = wxhelper::GlobalContext::GetInstance().mgr->InviteMemberToChatRoom(
                    room_id, wxids);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::ENABLE_WECHAT_LOG: {
            success = wxhelper::hooks::HookLog();
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::DISABLE_WECHAT_LOG: {
            success = wxhelper::hooks::UnHookLog();
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::CREATE_CHATROOM: {
            std::vector<std::wstring> wxids = GetArrayParam(j_param, "memberIds");
            success = wxhelper::GlobalContext::GetInstance().mgr->CreateChatRoom(wxids);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::QUIT_CHATROOM: {
            std::wstring room_id = GetWStringParam(j_param, "chatRoomId");
            success = wxhelper::GlobalContext::GetInstance().mgr->QuitChatRoom(room_id);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::SEND_FORWARD_MSG: {
            INT64 msg_id = GetINT64Param(j_param, "msgId");
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            success = wxhelper::GlobalContext::GetInstance().mgr->ForwardMsg(msg_id, wxid);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::GET_SNS_FIRST: {
            success = wxhelper::GlobalContext::GetInstance().mgr->GetSNSFirstPage();
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::GET_SNS_NEXT: {
            UINT64 snsid = GetUINT64Param(j_param, "snsId");
            success = wxhelper::GlobalContext::GetInstance().mgr->GetSNSNextPage(snsid);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::ADD_MSG_FAVOUR: {
            UINT64 msg_id = GetUINT64Param(j_param, "msgId");
            success = wxhelper::GlobalContext::GetInstance().mgr->AddFavFromMsg(msg_id);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::ADD_IMG_FAVOUR: {
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            std::wstring image_path = GetWStringParam(j_param, "imagePath");
            success = wxhelper::GlobalContext::GetInstance().mgr->AddFavFromImage(
                    wxid, image_path);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::CHECK_PERSON_INFO: {
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            common::ContactProfileInner profile;
            success = wxhelper::GlobalContext::GetInstance().mgr->GetContactByWxid(wxid,
                                                                                   profile);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            if (success == 1) {
                nlohmann::json contact_profile = {
                        {"account",   profile.account},
                        {"headImage", profile.head_image},
                        {"nickname",  profile.nickname},
                        {"v3",        profile.v3},
                        {"wxid",      profile.wxid},
                };
                ret_data["data"] = contact_profile;
            }
            output = ret_data.dump();
            break;
        }

        case common::DW_ATTACH_FILE: {
            UINT64 msg_id = GetUINT64Param(j_param, "msgId");
            success = wxhelper::GlobalContext::GetInstance().mgr->DoDownloadTask(msg_id);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::SEND_FORWARD_GZH_MSG: {
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            std::wstring appname = GetWStringParam(j_param, "appName");
            std::wstring username = GetWStringParam(j_param, "userName");
            std::wstring title = GetWStringParam(j_param, "title");
            std::wstring url = GetWStringParam(j_param, "url");
            std::wstring thumburl = GetWStringParam(j_param, "thumbUrl");
            std::wstring digest = GetWStringParam(j_param, "digest");
            success = wxhelper::GlobalContext::GetInstance().mgr->ForwardPublicMsg(
                    wxid, title, url, thumburl, username, appname, digest);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::SEND_FORWARD_GZH_ID_MSG: {
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            UINT64 msg_id = GetUINT64Param(j_param, "msgId");
            success = wxhelper::GlobalContext::GetInstance().mgr->ForwardPublicMsgByMsgId(
                    wxid, msg_id);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::DECODE_IMG_FILE: {
            std::wstring file_path = GetWStringParam(j_param, "filePath");
            std::wstring store_dir = GetWStringParam(j_param, "storeDir");
            success = wxhelper::GlobalContext::GetInstance().mgr->DecodeImage(
                    file_path, store_dir);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::DW_VOICE_FILE: {
            UINT64 msg_id = GetUINT64Param(j_param, "msgId");
            std::wstring store_dir = GetWStringParam(j_param, "storeDir");
            success = wxhelper::GlobalContext::GetInstance().mgr->GetVoiceByDB(
                    msg_id, store_dir);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::SEND_CUSTOM_EMJ: {
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            std::wstring file_path = GetWStringParam(j_param, "filePath");
            success = wxhelper::GlobalContext::GetInstance().mgr->SendCustomEmotion(file_path,
                                                                                    wxid);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::SEND_APPLET_MSG: {
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            std::wstring waid_concat = GetWStringParam(j_param, "waidConcat");
            std::string waid = GetStringParam(j_param, "waid");
            std::string app_wxid = GetStringParam(j_param, "appletWxid");
            std::string json_param = GetStringParam(j_param, "jsonParam");
            std::string head_url = GetStringParam(j_param, "headImgUrl");
            std::string main_img = GetStringParam(j_param, "mainImg");
            std::string index_page = GetStringParam(j_param, "indexPage");

            std::wstring waid_w = wxhelper::Utils::UTF8ToWstring(waid);

            success = wxhelper::GlobalContext::GetInstance().mgr->SendApplet(
                    wxid, waid_concat, waid_w, waid, app_wxid, json_param, head_url,
                    main_img, index_page);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::SEND_PAT_MSG: {
            std::wstring room_id = GetWStringParam(j_param, "receiver");
            std::wstring wxid = GetWStringParam(j_param, "wxid");
            success = wxhelper::GlobalContext::GetInstance().mgr->SendPatMsg(room_id, wxid);
            ret_data = {
                    {"code", success},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        case common::OCR_IMG_FILE: {
            std::wstring image_path = GetWStringParam(j_param, "imagePath");
            std::string text;
            success = wxhelper::GlobalContext::GetInstance().mgr->DoOCRTask(image_path, text);
            ret_data = {
                    {"code", success},
                    {"data", text},
                    {"type", type},
                    {"msg",  "success"}};
            output = ret_data.dump();
            break;
        }

        default:
            ret_data = {
                    {"code", 200},
                    {"data", {}},
                    {"type", type},
                    {"msg",  "Not support opcode"}};
            output = ret_data.dump();
    }
}