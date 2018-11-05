function populateCmtList() {
  project_id=window.location.href.substr(window.location.href.lastIndexOf('/')+1)
    $.get("/codereviewer/get-comment/"+project_id)
      .done(function(data) {
          var list = $("#comment-block");
          list.html('')
          for (var i = 0; i < data.comments.length; i++) {
              var cmt = data.comments[i];
              var new_cmt = $(cmt.html);
              list.append(new_post);
              var postCmtList = $("#cmt-list-"+post.id);
              postCmtList.html('')
              for(var j=0;j<post.comments.length;j++){
                var cmt = post.comments[j];
                postCmtList.append($(cmt.html));
              }
          }
      });
}
<pre>
  {% for line in codes %}
    <code class="java">
      {{ line }}
    </code>
  {% endfor %}
</pre>

$(document).ready(function() {
  $("#addCmtButton").click(function() {
    $("#addCmtButton").after('<input type="text" id="textInput" value="">');
  });
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
