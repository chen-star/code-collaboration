# Backlog 2

| Task                    | Time | Person  |
|-------------------------|------|---------|
| Member invitation       | 4h   | jinyil1 |
| Message box             | 5h   | jinyil1 |
| Multiple-file uploading | 4h   | jinyil1 |
| Project tree            | 5h   | jinyil1 |
| Code Review (comments, marks)|4h|weitongz|
| Real-time Interaction|5h|weitongz|
| Deployment*|5h|weitongz|
| Search bar supported |5h|wenxuanx|
| Statistic dashboard |4h|wenxuanx|
| Minor update on the design of UI |2h|wenxuanx|
| Programming language diversity (syntax highlight) |3h|jiaxinc1|
| Register & login with GitHub account |4h|jiaxinc1|
| Get project from GitHub |5h|jiaxinc1|


# Task specifications
1. Member invitation. 

A project owner can invite users to join a repository. Each invitation should send out a message. The implementation requires `views.py`, `forms.py`, `models.py`, `repo.html`, and `home.html`.

2. Message box

Message box should contain invitation messages sent from the project owner to the user. Unread messages should be in bold. The implementation requires `views.py`, `forms.py`, `models.py`, `repo.html`, and `home.html`.

3. Multiple-file uploading

Upload a file folder to a newly created project repository. The implementation requires `views.py`, `forms.py`, `models.py`, `repo.html`.

4. Project tree

Convert the file folder structure to a project structure tree in the webpage. The implementation requires `views.py`, `forms.py`, `models.py`, `repo.html`, and JavaScript scripts.

5. Code Review

Instead of adding comments to the sidebar, we will use a new design to add comments below that line of code, which is clearer and will show interactions between users. Also, reviewers can mark a line of code rather than leaving a comment. Requires `review.html` and related `js` files and database manipulation.

6. Real-time interaction

Reviewers will be able to see the comments and marks by other reviewers in the real-time. Requires `review.html` and related js files, with Ajax or web sockets.

* Deployment 

Deploy the web service to AWS, if time permits.

8. Registration & Login with GitHub Account

Using GitHub API to to register our website with user permission. After user login, our website can get necessary information from GitHub. We will implement this functionality by using GitHub API in views.py. We will also change our html page in static file.

9. Get project from GitHub

User can choose to upload source files from their local machines or from their GitHub Account. If a user choose to upload from GitHub, our website will get project directly from GitHub repository. This functionality will also be served within views.py by modifying the functions which generate project in our website.

1. programming language diversity (syntax highlight)

In sprint 1, our website just supported the Java syntax highlighting. In order to make website more useful, we will support more language highlighting. To implement this function, we will search if there is any available `js` package can be used. If not, we will implement this function by ourselves via `js`.

11. Search bar

User will be able to search either full or ambiguous file name. A suggestion dropdown menu will show all related results for user to access. One approach doing this functionality is to get a list of files belongs to this particular user in ` views.py ` and narrow down the result aimed by the regular expression. 

12. Statistic dashboard

Every user will be able to view his/her own stats as well as look up other users'. This dashboard supports real-time reflection. Any displaying information will be auto updated with AJAX.

13. Minor update on the design of the UI

UI may be change in order to achieve the uniform design.