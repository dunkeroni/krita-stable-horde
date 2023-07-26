def getToolTips():
	# Tooltips definitions
	toolTips = {}
	
	#basic
	toolTips['priceCheck'] = "Asks the Horde how much Kudos the current generation settings would cost\nTakes 2s to avoid spamming.\nAuto updates when relevant settings change."
	toolTips['generateButton'] = "Generate an image, covering up the current image with a new layer"
	toolTips['maskButton'] = "Creates a mask layer to draw on"
	toolTips['img2imgButton'] = "Generate an image, using the current image and mask as input"
	toolTips['denoise_strength'] = "Adjust the strength of the denoiser. \nHigher values will change the image more, lower will stay closer to the original."
	toolTips['CFG'] = "Higher values will make the result closer to the prompt, but may result in burnt images if too high. \nLower values will be more creative but can be blurry and less defined. \nLiterally this value affects how the prompt and unconditioned input (negative prompt if supplied) affects the result of each step."
	toolTips['SizeRange'] = "Images will always try to generate with the shorter side at least minSize pixels, but stopping if the larger side exceeds maxSize pixels."
	toolTips['seed'] = "The seed used to generate the image. \nLeave blank for a random seed. Enter a previous seed to generate the same image again, or a similar image with small changes to the settings."
	toolTips['model'] = "The model used to generate the image. \nThe number next to the model name denotes the number of workers in the horde that are currently offering that model."
	toolTips['sampler'] = "The sampler used to generate the image. \nDifferent samplers can result in different levels of detail, but may require changes to steps or CFG."
	toolTips['numImages'] = "The number of images to generate. \nConcurrency in the User tab will show how many images you can generate at one time."
	toolTips['steps'] = "The number of steps to run the model for. \nHigher values can increase detail for some samplers, but euler_a will just keep changing the entire image instead."
	toolTips['highResFix'] = "Generates the image at a lower resultion to begin, and then upscales to the target size to finish the generation. \nImproves the composition of images that are larger than 640 pixels in either direction."
	toolTips['prompt'] = "Describe the image you want to generate here."
	toolTips['negativePrompt'] = "Describe elements of an image that you don't want to generate here. \nKeep in mind that this only works if the things you describe are things that the model understands. Putting in a huge list of 'bad quality' synonyms is a waste of time for most models."
	toolTips['postProcessing'] = "Apply a post-processing filter to the generated image. \nGFPGAN and Codeformers are both face fixers."
	toolTips['facefixer_strength'] = "Adjust the strength of the face fixer. \nHigher values will change the image more, lower will stay closer to the original."
	toolTips['upscale'] = "Upscaler to use on the generated output. \nThe result will be scaled down to fit within the document selection.\nIit is recommended to use this in conjunction with MaxSize in order to generate a smaller image and then upscale past the selection size."
	toolTips['statusDisplay'] = "Displays the current status of the generation, \nas well as other information updates when certain events happen."
	toolTips['cancelButton'] = "Cancel the current generation and enable all input fields again. \nUseful if a generation goes stale or some error sticks the UI."
	
	#advanced
	toolTips['maxWait'] = "The maximum amount of time to wait for a result before giving up and canceling the request."
	toolTips['clip_skip'] = "Makes the prompt->embedding translation less precise by skipping the last layers of the CLIP model. \nCan make results better or more consistent on some models (particularly ones heavily based on the illegal NovelAI leaked model)."
	toolTips['nsfw'] = "Enable NSFW results. Leaving False may cause some results to be filtered if NSFW content is detected."
	toolTips['karras'] = "Magic. Improves generation with fewer steps."
	toolTips['useRealInpaint'] = "Force trigger Inpaint instead of preferred Img2Img mode. For debugging."
	toolTips['shareWithLAION'] = "Share your generated images with the LAION database to help training in the future. \nThis will not share any of your personal information, only the generated images. Reduces kudos cost."
	
	#user
	toolTips['apikey'] = "Your API key. Identifies you so that you can use your stored up kudos. \nYou can request an API key on the AI Horde website. \nDo not lose it, and do not share it with others."
	toolTips['userID'] = "Your user ID. This is used to identify you to the AI Horde."
	toolTips['workerIDs'] = "List of the IDs of the workers you are currently running on the horde."
	toolTips['kudos'] = "The amount of kudos you currently have. \nTakes a while to update on the server, so it may not reflect recent changes."
	toolTips['trusted'] = "Whether or not you are a trusted worker. Untrusted workers earn half kudos. \nTakes about a week to get trusted status, at which point the withheld kudos is given back."
	toolTips['concurrency'] = "The number of images you can generate at one time."
	toolTips['requests'] = "The number of requests you have made to the AI Horde."
	toolTips['contributions'] = "The number of contributions you have made to the AI Horde."
	toolTips['refreshUserButton'] = "Refresh your user information. This will update all of the above fields."
	toolTips['preferredWorkers'] = "List of worker IDs that you prefer to run on. Separate IDs with commas. \nCopy your own worker ID from above if you want to run images from your own computer."

	#experimental
	#toolTips['inpaintMode'] = "Temporary settings that add extra functionality for testing: 0 = Img2Img PostMask, 1 = Img2Img PreMask, 2 = Img2Img DoubleMask, 3 = Inpaint Raw Mask"
	
	#results
	toolTips['groupSelector'] = "Select which group of results to view. \nEach generation creates a new group, regardless of how many images were requested."
	toolTips['nextResult'] = "View the next result in the current group."
	toolTips['prevResult'] = "View the previous result in the current group."
	toolTips['deleteButton'] = "Delete the current result."
	toolTips['deleteAllButton'] = "Delete all results in the current group."
	toolTips['genInfo'] = "Information about the current result."

	return toolTips

def addToolTips(allWidgets):
	# Tooltips definitions
	toolTips = getToolTips()

	#for each widget in the dictionary, add the tooltip
	for key in allWidgets:
		#only if the key is in the tooltips dictionary
		if key in toolTips:
			allWidgets[key].setToolTip(toolTips[key])
