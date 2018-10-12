# Collaborative Source Code Review
		

### Team member Andrew IDs:

jiaxinc1, wenxuanx, weitongz, jinyil1

## Selected Original Project Proposal

The concept of the project was initially brought about from incredibly common issues faced by vulnerability (bug) hunters. Bug hunters oftentimes work in groups to perform analysis on source code, but tend to use inefficient systems of collaboration like Pastebin and group messaging systems to share their knowledge. Two reviewers looking at the same code might come across potentially vulnerable sections independently, but lack the ability to record and share their thoughts with each other. Additionally, code navigation in giant codebases is very difficult without some kind of rich navigation system provided by an IDE to hop between files easily. Currently, we believe there is no good solution that combines rich navigation with collaborative functionality.

The goal of this project is to provide a platform for code reviewers to collaborate and share code from large codebases. Reviewers can upload source code or link to a Github repo, which gets processed on the backend for metadata information. We will primarily focus on supporting C/C++ source code for several reasons. Bug hunters deal with these languages when looking for vulnerabilities, but the nature of the language makes navigation between files in large projects difficult. Our solution will be our backend platform that will do source code analysis to create a mapping database of definitions to their usages. Users can open an online source code viewer for an IDE-like experience including cross-references (places where variables/functions are referenced in other parts of the source code) and structure definitions of objects. This information is important for reviewers as it allows them to follow how data is passed around during execution. In addition, reviewers can also flag lines of code that may be interesting and optionally add a note on the side detailing their findings. Groups of reviewers can see and comment on these points of interest.

With these features, reviewers can collaboratively perform analysis of source code without the issue of work duplication. As of right now, there are multiple vulnerability researchers that are very interested in using this project for their day-to-day work. We believe this web app will allow reviewers to quickly achieve their code review goals, whether it be vulnerability hunting or developer code review.

## Modified Proposal

The concept of the project was initially brought about from incredibly common issues faced by vulnerability (bug) hunters. Bug hunters oftentimes work in groups to perform analysis on source code, but tend to use inefficient systems of collaboration like Pastebin and group messaging systems to share their knowledge. Two reviewers looking at the same code might come across potentially vulnerable sections independently, but lack the ability to record and share their thoughts with each other. Additionally, code navigation in giant codebases is very difficult without some kind of rich navigation system provided by an IDE to hop between files easily. Currently, we believe there is no good solution that combines rich navigation with collaborative functionality.

The goal of this project is to provide a platform for code reviewers to collaborate and share code from large codebases. Reviewers can upload source code or link to a Github repo, which gets processed on the backend for metadata information. We will primarily focus on supporting **Java and** C/C++ source code for several reasons. Bug hunters deal with these languages when looking for vulnerabilities, but the nature of the language makes navigation between files in large projects difficult. Our solution will be our backend platform that will do source code analysis to create a mapping database of definitions to their usages. Users can open an online source code viewer for an IDE-like experience including cross-references (places where variables/functions are referenced in other parts of the source code) and structure definitions of objects. This information is important for reviewers as it allows them to follow how data is passed around during execution. In addition, reviewers can also flag lines of code that may be interesting **or problematic** and optionally add a note on the side detailing their findings. Groups of reviewers can see and comment on these points of interest. **Coders (who upload the source code) can select and invite reviewers to review the code. Users will receive notification about new invitations, new comments, etc. Users have a clear project navigation via the side bar of projects' structure. Reviewers of the same file/project can see the real-time comments and edits from others.**

With these features, reviewers can collaboratively perform analysis of source code without the issue of work duplication. As of right now, there are multiple vulnerability researchers that are very interested in using this project for their day-to-day work. We believe this web app will allow reviewers to quickly achieve their code review goals, whether it be vulnerability hunting or developer code review.


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


* **Upload to Github** *(backend: jinyil1, frontend: wenxuanx)*

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
![screenshot](img/registration.png)

* user home page, notification box 
![screenshot](img/home.png)
Click on the "new message" to go to the code review page.
"Log out" will take you back to the login page.

* user profile page, view and edit profile info
![screenshot](img/account.png)
You may upload source code and select reviewer.

* code review page
![screenshot](img/code_review.png)
"Exit reviewing" will take you back to the home page.


## APIs

*  https://help.github.com/articles/creating-and-highlighting-code-blocks/

* https://github.com/substack/highlight-syntax

* https://highlightjs.org/

* https://codepen.io/peternguyen/pen/nDEFI

* https://pusher.com/tutorials/live-comments-javascript/ 

* https://about.sourcegraph.com/docs/

* https://plot.ly/python/
