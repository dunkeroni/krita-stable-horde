# Krita Stable Horde features
List of existing and planned features  

## Parallel Procesing
Make generation process act on currently selected Document, and retain that document connection throughout.  
    Handle retentive objects through a new hordeDoc class in fontend. Move functions out of Widget.  
Connect cancelation button to currently viewed Document.  
Split Inpaint/Img2Img mode buttons and/or simplify so that state can be determined from active document.  
    Change mask mode to create/remove mask layer based on current document status.  
    Create a handling trigger based on Document change?  
Track concurrency/kudos/active generations in status panel.  
    Move all update messages to the log view and keep current status organized.  

## Advanced:
~~CLIP skip~~  
    added, but appears to be broken on the horde right now.  
Premade prompts  
    Custom positive+negative saved prompts  
    Community prompts from horde  
Add Control Net  
    save/clear control net image from selection?  

## Interfacing:
Auto-mask selection?  
    Currently a selection is required before switching to mask mode. Should not require.  

## Kudos:
Add kudos transfer (broke on last attempt)  
Created delayed trigger with dry-run kudos check on settings change  
    Current kudos calculation is out of date. Server uses neural network.  

## Known bugs that I can't be bothered to solve just yet:
Crashes if internet connection is lost while requesting.  
Errors on first load when API key is blank.  
Inpainting with some samplers (DDIM) causes a faulty request which errors on check.  
    This is a horde issue, not a plugin issue.  
    Workaround: use a different sampler.  
    Fix: Will add some restrictions to samplers in the future.  
Results Collector does not gracefully handle users deleting nodes manually.  