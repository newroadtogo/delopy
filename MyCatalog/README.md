
Item Catalog Application PACKAGE
======================

This package implements an item catalog applicaiton which provide the simle information about sport catalog and authorized people can edit its owne items.

SETUP
=====

 1. Install the VirtualBox. You can get it at
 
    https://www.virtualbox.org/wiki/Downloads
	
 2. Install the Vagrant. You can get it at
 
    https://www.vagrantup.com/downloads.html

 3. Clone the fullstack-nanodegree-vm. You can get it at
 
    https://github.com/udacity/fullstack-nanodegree-vm
	
 4. Launch the Vagrant VM, using following command
    
	$vagrant up

 5. Connect to the Vagrant VM, using the following command
    
	$vagrant ssh
 
 6. Install extra modules(flask_login, simplejson, google-oauth2-credentials and google_auth_oauthlib.flow), using following command
 
    §sudo pip install flask_login
	$sudo pip install simplejson
	$sudo pip install --upgrade google-api-python-client
    $sudo pip install --upgrade google-auth-oauthlib to install module 

 7. Apply the Google OAuth credential for the Web Application, get the Client ID and Client Key, and download the json file

    https://console.developers.google.com/
	
 8. Enable the Google People API

 9. Go to directory catalog, run following commands to set the enviroment
 
	$export FLASK_APP=MyCatalog
	$export FLASK_ENV=development
	
 10. Run the application with command 
 
    $flask run --host=0.0.0.0
 
 11. Open browser(IE, Google Chrome and so on), visit http://localhost:5000
 
 12. Try to view the items, login, edit and delete your own items 
 
 
 

CONTACT
=======

Please send bug reports, patches, and other feedback to
wjjmay81@gmail.com