To update the Dashboards :
* Have your Pull Request to this repo approved by a Gatekeeper.  This will launch a Github Action to rebuild the docker image hosting this amazing code.  Image will be committed to Artifactory.  Check the log in case of an error: https://github.sherwin.com/SW-CORP-IT/sw_plopsboard/actions
   * If the action fails, run it again manually (worked previously with Xray failures).  If it fails again, go talk to Srini/Boker/(insert new Delivery Automation team here).
* Once successful, you need to redeploy in Rancher.  Log into Rancher, prod->GCD Linux->gpodashprod->gpodashdeployment.  https://rancher.sherwin.com/p/local:p-nfd5k/workloads.  
  
  ![image](https://media.github.sherwin.com/user/407/files/b53239a6-0d27-4384-ab17-461fb422c82e)
  
* Once redeployed, Dashboard updates should be live at https://gpodash.sherwin.com/
  


