# Backlog 3

| Task                    | Time | Person  |
|-------------------------|------|---------|
| Improve message box|4h|jinyil1|
| Improve file tree|5h|jinyil1|
| Improve code review comments|5h|weitongz|
| Improve search bar|4h|wenxuanx|
| Improve statistic dashboard|4h|wenxuanx|
| Improve GitHub authentication and uploading|4h|jiaxinc1|
| Deployment to AWS|5h|weitongz|
| Migrate file system from local to S3|5h|jiaxinc1|
| Unit testing|5h|all members|

# Task specifications
1. Improve message box (jinyil1)

Connect messages in the message box to a repository review page with the file tree. Modify `views.py`, `models.py`, `repo.html`, and `base-home.html`.

2. Improve file tree (jinyil1)

Generate fully functioning file trees - After creating a new repo, a new tree should be generated; the buttons in a tree should be connected with a code file, and can navigate to the correct page and display. Modify `views.py`, `tree.js`, `review.html`, `home.html`, `repo.html`, and `base-home.html`.

3. Improve code review comments (weitongz)

Add comment flags to the lines with comments. Use indentations to imply the hierarchy between comments (is it a comment or a reply to a comment?). Modify JavaScript and the html code about commenting.

4. Deployment to AWS (weitongz)

Deploy the project to an AWS instance. 


5. Improve Github Authentication and uploading

Currently we can only upload one file from github repository, so in the sprint 3, we will implement upload whole project by using python embedded Github API. Also, binding github accounts with models of users will be re-implemented.

6. Migrate file system from local to S3

We will use S3 to store our file system. Considering with the growth of the size of repositories, local file system cannot satisfy our needs. S3 is a distributed storage system, so we will migrate local files onto S3.
