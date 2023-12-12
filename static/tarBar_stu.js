 $(document).ready(function() {
         let account=Server.account_url;
         document.getElementById("zy_id").href=("/users/stu_page/"+account);
         document.getElementById("zl_id").href=("/users/stu_info/"+account);
         document.getElementById("con_2").href=("/conference/conf_add_stu/"+account);
         document.getElementById("jr_2").href=("/journal/jn_add_stu/"+account);
         document.getElementById("pt_2").href=("/patent/patent_add_stu/"+account);
         document.getElementById("sf_2").href=("/software/soft_add_stu/"+account);
         document.getElementById("mo_2").href=("/monograph/mono_add_stu/"+account);
         document.getElementById("com_2").href=("/competition/comp_add_stu/"+account);
         document.getElementById("pr_2").href=("/program/prog_add_stu/"+account);
         document.getElementById("con_id_2").href=("/conference/conf_upload_stu/"+account);
         document.getElementById("jr_id_2").href=("/journal/jn_upload_stu/"+account);
         document.getElementById("pt_id_2").href=("/patent/patent_upload_stu/"+account);
         document.getElementById("sf_id_2").href=("/software/soft_upload_stu/"+account);
         document.getElementById("mo_id_2").href=("/monograph/mono_upload_stu/"+account);
         document.getElementById("new_id_2").href=("/news/news_upload_stu/"+account);
         document.getElementById("res_id_2").href=("/resource/resource_upload_stu/"+account);
         document.getElementById("conf_rec_stu_id").href=("/conference/conf_rec_stu/"+account);
         document.getElementById("jn_rec_stu_id").href=("/journal/jn_rec_stu/"+account);
 })

