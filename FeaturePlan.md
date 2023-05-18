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
Add Control Net  
    save/clear control net image from selection?  
### Results Collection:
Results interface in regular docker as its own tab.  
    ~~Dropdown list for result groups~~  
    ~~Buttons to iterate through current group~~  
    ~~Delete current result or delete all other results if desired~~  
    ~~Inpaint mask needs to be carried through to the results buffer~~  
    ~~Display generation info on currently selected result~~  
~~Horde interactor needs to pass results into requestor library where they are saved.~~  
~~Widget needs to switch to results tab when results are available and results > 1~~  

### Interfacing:
~~Generate on Selection instead of whole file resolution~~  
    ~~Adjustable max resolution for non-square selections~~  
    ~~Fit rectangle to next 64 multiple around selection~~  
    Auto-mask selection?  
        Currently a selection is required before switching to mask mode. Should not require.  

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
Results Collector does not gracefully handle users deleting nodes manually.  