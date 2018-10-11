# Collaborative Source Code Review
		

### Team member Andrew IDs:

jiaxinc1, wenxuanx, weitongz, jinyil1
	

## List of all functionality

* **Account management** *(backend: jinyil1, frontend: wenxuanx)*

	* User registration and login

	* User profile display and setting
	
	* Notification box/message center. For display invitations of new code reviewing and notification of one’s own code being reviewed by others.
	
	* Team creation and management: Only project manager has the permission to create, manage, and remove repositories. Project members must be selected by the manager and join the team through email invitation and verification. If the invitee is new to our website, he/she will receive an email and go through verification. Otherwise the invitee will receive a notification email and a “new message” in the notification box


* **Code review** *(backend: jiaxinc1, frontend: weitongz)*
	* Code representation with syntax highlighting (Java and C/C++)
	
	* Line-level comment: create, edit, delete comments. Tag comments according to type(to-do, delete, create, modify..) and priority(urgent, medium, normal)
	
	* Flag lines of code that may be interesting or problematic
	
	* Within the review of the same source code, reviewers can see the real-time edit from other users 


* **Code navigation** *(backend: jinyil1, frontend: weitongz)*

	* Function searching: when a user type in a keyword, it will automatically display all matched keywords in the file.

	* Project-level code navigation (navigating to a specific function within a project)

	* File-level code navigation (navigating to a specific function within a file) 

	The nature of the language makes navigation between files in large projects difficult. Our solution will be our backend platform that will do source code analysis to create a mapping database of definitions to their usages. Key combination triggers a link to source code page of the selected syntax keyword. 

	Navigating from where the methods and functions are used to where they are defined and implemented. 
	
	
* **Code review statistics dashboard** *(backend: jiaxinc1, frontend: weitongz)*
	* Project-level statistics dashboard
		* Present a summary of project-level statistics
			* using line charts
			* using pie charts
		* Grouping the number of review comments
			* by time
			* by task priority tag
			* by who made comments
			* by whose codes were commented
	* User-level statistics dashboard


* **Upload to Github** *(backend: jinyil1, frontend: wenxuanz)*

	Reviewers can upload source code or a link to a Github repo, which gets processed on the backend for metadata information. 
	
	
## List of Data Models
* **User**

	userid, user_name, email, password, team, photo, repositories**

* **Team**

	teamid, team_name, repositories*, users*, manager (FK)
	
* **User_Repository**

	user, repository
	
* **Repository**

	each project will have a code repository
	
	repo_id, users, files, project_name, create_time, modified_time, modify_frequency

* **File**

	file_id, repository (FK), content, last_modified_time
	
* **Comments**

	Reviewer can select a type for a comment, implying what type of tasks the code should fulfill
	
	file_id, line_num, last_modifier (FK), content, last_modified_time, types(delete, modify, 	create, to-do), priority_tag(urgent, medium, normal)

* **Word**

	word_id, word, file (FK), line_num, frequency
	
* **Notification**

	receiver_id, datetime, content, type (new code to review, new review from other reviewers on the     reviewed code, new review on your code, etc)
	
* **Keyword**

	keyword_id, keyword, group, color

## Wireframes or HTML
* user login page
![screenshot](img/login.png)
Go to register page by clicking "register an account". By now you may login with any email address and password.    
![screenshot](img/login2.png)

* user register page
![screenshot](img/register.png)

* user home page, notification box 
![screenshot](img/home.png)
Click on the "new message" to go to the code review page.
"Log out" will take you back to the login page.

* user profile page, view and edit profile info
![screenshot](img/account.png)
You may upload source code and select reviewer.

* code review page
![screenshot](img/code/review.png)
"Exit reviewing" will take you back to the home page.


## APIs

*  https://help.github.com/articles/creating-and-highlighting-code-blocks/

* https://github.com/substack/highlight-syntax

* https://highlightjs.org/

* https://codepen.io/peternguyen/pen/nDEFI

* https://pusher.com/tutorials/live-comments-javascript/ 

* https://about.sourcegraph.com/docs/

* https://plot.ly/python/