# History
## Krita Plugin 2.X

### 2.0.2 - Hotfix
- Updated API call backend to prevent connection issues with new aihorde.net domain and redirects
- Added inpainting modes in Experimental tab of interface (bonus since this is what I was testing when I needed to apply the API fix)

### 2.0.1
- more architecture fixes to allow for better feature expansion in the future
- added Share With LAION database option
- included link to git repository for update message

### 2.0.0
Changes
- Changed interface to Docker instead of popup window  
- Inpainting mode is now done with masked img2img. This allows low denoise since it uses the original image. Real inpaint will be fixed later on.  
#### Added features:
- Model Selection option  
- Sampler Selection option  
- Negative Prompts  
- Highres Fix  
- Karras  
- Post Processors  
- CLIP skip  
- Generate on Selection (Txt2Img/Img2Img/Inpainting)  
- Inpainting Mask Mode  
- Min/Max Resolution limits  
- User Information (kudos, stats)  
- Debug and information logging via the built-in Krita logger docker  
- On-the-fly kudos calculation added to the generate buttons
- Lots of backend organization and restructuring

#### Known Issues:
- Crashes if internet connection is lost while request is active.  
- Throws an error on startup on when the API key field is blank.   

## Original Repo 1.X versions:

### 1.3.4
Changes
- The generated images are now transferred via Cloudflare r2.

### 1.3.3
Changes
- The new parameter r2 is transferred with value False. This disables for now the new Cloudflare r2 image download.

### 1.3.2
Changes
- Now detailed error messages are displayed. Before only the standard HTTP error messages.

### 1.3.1
Changes
- In the case no worker is available for image generation, now a message is displayed.
- Minimum size has been reduced from 512x512 to 384x384.

Bugfixes
- In the dialog init strength selector was not disabled in mode inpainting.
- In the dialog in mode inpainting was not checked if a layer with an inpainting image exists.

### 1.3.0
Changes
- Inpainting is supported now.

### 1.2.0
Changes
- Now images with sizes between 512x512 and 1024x1024 can be generated. Before only 512x512.
- The dialog has now two tabs to make the layout cleaner.
- It is now checked, if support for webp in Qt5 exists. On some Linux distributions the support is missing and needs to be installed manually.

### 1.1.1
Bugfixes
- When using img2img in some cases an error 400 occurred.
- It was not checked, if a prompt was entered. If it was missing, an error 400 occurred.

### 1.1.0
Changes
- img2img is now supported.

Bugfixes
- If the dialog was closed via the cross, the generation was not stopped.

### 1.0.1
Changes
- Now status information is displayed after generation start.

### 1.0.0
- Initial version.
