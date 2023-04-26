# Krita Stable Horde features
List of existing and planned features  
## Previous Capabilities
1.0.0 - Forked from https://github.com/blueturtleai/krita-stable-diffusion - last commit 80b9a1d on Dec 12, 2022  
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
Clean up structure dependencies to make more sense  
Centralize API calls  
~~Hide API key by default~~  
Break krita_stablehorde.py into functional modules  
    Current image + settings ==> Resolve image/mask/mode ==> preformat image scaling ==> send to horde  
    receive from horde ==> add results to layers and group ==> apply selected layer to current image  
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
### Interfacing:
Generate on Selection instead of whole file resolution  
    Adjustable max resolution for non-square selections  
    Fit rectangle to next 64 multiple around selection  
    Auto-mask selection?  
~~Settings window permanently fixed as toolbar~~  
~~User info from API key (kudos, generation statistics, etc.)~~  
    add kudos transfer  
### Known bugs that I can't be bothered to solve just yet:
Crashes if internet connection is lost while requesting.  
