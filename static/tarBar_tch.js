    $(document).ready(function() {
        let account=Server.account_url;
         document.getElementById("mn_1").href=("/users/tch_page/"+account);
        document.getElementById("mn_2").href=("/users/tch_info/"+account);
        document.getElementById("con_id").href=("/conference/conf_upload_tch/"+account);
        document.getElementById("jr_id").href=("/journal/jn_upload_tch/"+account);
        document.getElementById("pt_id").href=("/patent/patent_upload_tch/"+account);
        document.getElementById("sf_id").href=("/software/soft_upload_tch/"+account);
        document.getElementById("mo_id").href=("/monograph/mono_upload_tch/"+account);
        document.getElementById("pr_id").href=("/program/prog_upload_tch/"+account);
        document.getElementById("ho_id").href= ("/honor/honor_upload_tch/"+account);
        document.getElementById("co_id").href=("/course/course_upload_tch/"+account);
        document.getElementById("com_id").href=("/competition/comp_upload_tch/"+account);
        document.getElementById("new_id").href=("/news/news_upload_tch/"+account);
        document.getElementById("res_id").href=("/resource/resource_upload_tch/"+account);
        document.getElementById("con_1").href=("/conference/conf_add_tch/"+account);
        document.getElementById("jr_1").href=("/journal/jn_add_tch/"+account);
        document.getElementById("pt_1").href=("/patent/patent_add_tch/"+account);
        document.getElementById("sf_1").href=("/software/soft_add_tch/"+account);
        document.getElementById("mo_1").href=("/monograph/mono_add_tch/"+account);
        document.getElementById("pr_1").href=("/program/prog_add_tch/"+account);
        document.getElementById("co_1").href=("/course/course_add_tch/"+account);
        document.getElementById("com_1").href=("/competition/comp_add_tch/"+account);
        document.getElementById("ho_1").href=("/honor/honor_add_tch/"+account);
        document.getElementById("conf_rec_tch_id").href=("/conference/conf_rec_tch/"+account);
        document.getElementById("jn_rec_tch_id").href=("/journal/jn_rec_tch/"+account);
    });