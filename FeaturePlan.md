# Krita Stable Horde features
List of existing and planned features  
## Previous Capabilities
1.3.4 - Forked from https://github.com/blueturtleai/krita-stable-diffusion - last commit 80b9a1d on Dec 12, 2022  
    Floating settings window  
        Modes: txt2img, img2img, inpainting  
        Basics: NSFW, Seed, Prompt  
        Advanced: init strength (denoise), prompt strength (CFG), steps, API key, timeout  
    All generations done at workspace resolution  
    Inpainting mask created via eraser tool (background becomes mask)  
    Single model only (stable diffusion 1.5?)  
## Desired Features
### Organization:
~~Move everything out of a single file~~  
~~Clean up structure dependencies to make more sense~~  
~~Centralize API calls~~  
~~Hide API key by default~~  
~~Break krita_stablehorde.py into functional modules~~  
    ~~Current image + settings ==> Resolve image/mask/mode ==> preformat image scaling ==> send to horde~~  
    ~~receive from horde ==> add results to layers and group ==> apply selected layer to current image~~  
~~Change interface from floating window on plugin activation to dockers~~  
    ~~Automatically available on startup~~  
    ~~Settings on left panel~~  
    Results interaction on bottom?  
### Basics:
~~Model selection~~  
    ~~filtering/sorting?~~  
    ~~list worker count with model name~~  
~~Negative Prompt~~  
~~Sampler selection~~  
### Advanced:
~~Highres Fix option~~  
~~Karras (default on)~~  
~~Post Processors~~  
~~CLIP skip~~  
    added, but appears to be broken on the horde right now.  
Premade prompts  
    Custom positive+negative saved prompts  
    Community prompts from horde  
Multiple Image results  
    Need to organize results into layer groups  
    Create some interface to rotate through options. Invis unused layers in group.  
        Architectural note:  
        1. create an invisible layer for each request and group  
        2. queue up a worker per request  
        3. set worker to resolve its own interaction or cancelation with layer handler  
        4. Add interface bar for swapping through layers  
Add Control Net  
    save/clear control net image from selection?  
### Interfacing:
~~Generate on Selection instead of whole file resolution~~  
    ~~Adjustable max resolution for non-square selections~~  
    ~~Fit rectangle to next 64 multiple around selection~~  
    Auto-mask selection?  
    Inpainting Masks:  
        Intended Workflow:  
            1. Select rectangular area with normal selection box  
            2. Hit "Inpaint Mask" button  
            3. Draw mask inside selection with brush tool  
            4. Hit "Inpaint Img2Img"  
            5. Choose from results  
        Functional Backend (starts on "Inpaint Mask" trigger):  
            1. Check for selection, prompt warning if it does not exist
            2. Activate global selection layer
            3. Switch to brush tool --> wait for user to send i2i command
            4. Crop selection, invert, convert to greyscale mask image
            5. Disable global mask, change back to rectangular selection tool
            6. Generate images grom horde, hand back to user

~~Settings window permanently fixed as toolbar~~  
~~User info from API key (kudos, generation statistics, etc.)~~  
    add kudos transfer (broke on last attempt)  
### Known bugs that I can't be bothered to solve just yet:
Crashes if internet connection is lost while requesting.  
Errors on first load when API key is blank.  
Inpainting with some samplers (DDIM) causes a faulty request which errors on check.  
    This is a horde issue, not a plugin issue.  
    Workaround: use a different sampler.  
    Fix: Will add some restrictions to samplers in the future.