# Gen AI Powered Meeting Minute Generator 
## About this application

MoMGen is a tool that helps you analyze meeting transcripts and prepare structured documents within minutes.
Typically, when you have web meetings using MS Teams or Zoom, you can turn on the meeting transcripts which keeps track of the conversations and provides detailed dialogs based on time stamp. However, it is often difficult to review those transcripts and make a meaningful summary.

Modern tools like MS Copilot comes up with meeting summary options. However, that never comes up with summary with intended purpose.
To make a meaningful and insightful meeting minutes you need to understand the context and intent behind the meeting and structure your output document accordingly.

MoMGen does this exactly. It allows you to create a structure of the output document based on your need and allow Gen AI to fill out the different sections based on your intent.

This application is a demo app that shows the power of SAP's Business AI offering - where the core AI services are used from SAP BTP AI Core and vector embeddings are stored on SAP HANA Cloud Vector Engine. The service layer is built on LangChain using SAP AI Core proxy that gives flexibility to chose the LLM model. By default GPT3.5 is chosen. The UX is developed using SAP Build Apps - LCNC platform and the app is deployed on SAP BTP Cloud Foundry environment. The app can be accessed securely via the SAP Build Workzone Standard launchpad.

## How to run
App can be accessed via the following URL:
https://rise-setup-sh397zlr.launchpad.cfapps.us10.hana.ondemand.com/site?siteId=c8a7c371-da6a-45a5-94e5-a386e89311e1#buildapps67575-open?sap-ui-app-id-hint=saas_approuter_buildapps67575

Please contact: shibaji.chandra@sap.com if you need access.