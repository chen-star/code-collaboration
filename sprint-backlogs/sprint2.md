# Backlog 2

| Task                    | Time | Person  |
|-------------------------|------|---------|
| Member invitation       | 4h   | jinyil1 |
| Message box             | 5h   | jinyil1 |
| Multiple-file uploading | 4h   | jinyil1 |
| Project tree            | 5h   | jinyil1 |
| Code Review (comments, marks)|4h|weitongz|
| Real-time Interaction|5h|weitongz|


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
Instead of adding comments to the sidebar, we will use a new design to add comments below that line of code, which is clearer and will show interactions between users. Also, reviewers can mark a line of code rather than leaving a comment. Requires `review.html` and related js files and database manipulation.

6. Real-time interaction
Reviewers will be able to see the comments and marks by other reviewers in the real-time. Requires `review.html` and related js files, with Ajax or web sockets.