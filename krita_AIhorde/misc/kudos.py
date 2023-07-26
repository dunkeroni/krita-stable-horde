"""DEPRECATED
New system uses a neural network model on the server side to judge kudos requirement.
The network estimates the actual compute time required for a job based on the parameters.
The calculation can no longer be done locally from a python instance within Krita."""
import math

doesDenoiseStrengthAffectSteps = False #This is a server-side bug. Switch to true when fixed.

def calculateKudos(width, height, steps, samplerName, hasSourceImage, isImg2Img, denoisingStrength, postProcessors, usesControlNet, prompt, shareWithLaionEnabled):
	result = math.pow((width * height) - (64 * 64), 1.75) / math.pow((1024 * 1024) - (64 * 64), 1.75)
	steps = getAccurateSteps(steps, samplerName, hasSourceImage, isImg2Img, denoisingStrength)
	kudos = round(((0.1232 * steps) + result * (0.1232 * steps * 8.75)) * 100) / 100

	for i in range(0, len(postProcessors)):
		kudos = round(kudos * 1.2 * 100) / 100

	if usesControlNet:
		kudos = round(kudos * 3 * 100) / 100

	weightsCount = countParentheses(prompt)
	kudos += weightsCount

	if hasSourceImage:
		kudos = kudos * 1.5

	if 'RealESRGAN_x4plus' in postProcessors:
		kudos = kudos * 1.3
	if 'RealESRGAN_x4plus_anime_6B' in postProcessors:
		kudos = kudos * 1.3
	if 'CodeFormers' in postProcessors:
		kudos = kudos * 1.3

	hordeTax = 3
	if shareWithLaionEnabled:
		hordeTax = 1
	if kudos < 10:
		hordeTax -= 1
	kudos += hordeTax

	return round(kudos*100)/100

def getAccurateSteps(steps, samplerName, hasSourceImage, isImg2Img, denoisingStrength):
	if samplerName in ['k_dpm_adaptive']:
		return 50
	if samplerName in ['k_heun', 'k_dpm_2', 'k_dpm_2_a', 'k_dpmpp_2s_a']:
		steps *= 2
	if hasSourceImage and isImg2Img and doesDenoiseStrengthAffectSteps:
		steps *= denoisingStrength
	return steps


def countParentheses(prompt):
	openP = False
	count = 0
	for i in range(0, len(prompt)):
		c = prompt[i]
		if c == "(":
			openP = True
		elif c == ")" and openP:
			openP = False
			count += 1
	return count