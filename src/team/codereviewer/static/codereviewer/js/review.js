
function populateCmtList() {
  project_id=window.location.href.substr(window.location.href.lastIndexOf('/')+1)
    $.get("/codereviewer/get-comments/"+project_id)
      .done(function(data) {
          var list = $("#comment-block");
          list.html('');
          var total_lines = parseInt(document.getElementById('line_num').value);
          var cmt_list =[]
          for (var i= 0; i<data.comments.length;i++){
            cmt_list.push(data.comments[i].line_num);
          }
          for (var i = 0; i < total_lines; i++) {
            console.log('add + for '+i);
            var new_html = '<div class="addCmtPlus"><p style="font-family: sans-serif;margin-bottom: 0rem;line-height:1;"><a id="addCmtButton_"'+i+'>+</a></p>"';

            if(cmt_list.includes(i)){
              var cmt = data.comments[i];
              new_html=new_html+$(cmt.html);
            }
            list.append(new_html);
          }
      });
}
function reply_click(clicked_id){
  var index = 0;
     $("#clicked_id").after('<input type="text" id="cmt_content_'+index+'" value=""><button id="sendCmt_'+index+'" type="submit" class="btn btn-success" style="font-size:15px;line-height:1.2;padding: 0.15rem .5rem;">Send</button>');
}
// $(document).on("click", ".addCmtPlus", function(event){
//   $("#addCmtButton").click(function() {
//     $("#addCmtButton").after('<input type="text" id="cmt_content_'+index+'" value=""><button id="sendCmt_'+index+'" type="submit" class="btn btn-success" style="font-size:15px;line-height:1.2;padding: 0.15rem .5rem;">Send</button>');
//   });
$(document).ready(function() {
  populateCmtList();
});
//
// $(document).on("click", ".cmt-btn", function(event){
//   event.preventDefault();
//   selector = "#id_commentcontent_"+this.id;
//   if($(selector).val()===null ||$(selector).val()===""){
//     alert("Please enter comment!");
//   }else{
//     $.post("/grumblr/add-comment", {
//       'commentcontent':$(selector).val(),
//       "commented-post":this.id,
//     })
//       .done(function(data) {
//           console.log("sent cmt");
//           var cmt_list = $("#cmt-list-"+this.id);
//           populateList();
//           $('#messages').empty();
//           for(var i = 0; i < data.msg.length; i++) {
//             $('#messages').append('<li>' + data.msg[i] + '</li>');
//           }
//           $(selector).val('');
//       });
//   }
//
// });
