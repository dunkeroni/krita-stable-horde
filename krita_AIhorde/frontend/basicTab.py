from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ..misc import range_slider
from ..core import hordeAPI

def addBasicTab(tabs: QTabWidget, dialog):
    qDebug("Creating Basic tab elements")
    basic = {} #pointer to dictionary
    basicTab = buildBasicTab(basic, dialog)
    tabs.addTab(basicTab, "Basic")

    return basic #dictionary of tab elements

def buildBasicTab(basic, dialog):
    # ================ Basic Tab ================
		tabBasic = QWidget()
		layout = QFormLayout()

		# Generate
		generateButton = QPushButton("Generate")
		generateButton.setStyleSheet("background-color:#A04200;")
		priceCheck = QPushButton("checkKudos")
		layout.addRow(priceCheck, generateButton)
		basic['priceCheck'] = priceCheck
		basic['generateButton'] = generateButton

		# Mask and Img2Img buttons
		maskButton = QPushButton("Mask")
		img2imgButton = QPushButton("Img2Img")
		maskButton.setStyleSheet("background-color:#015F90;")
		img2imgButton.setStyleSheet("background-color:#015F90;")
		layout.addRow(maskButton, img2imgButton)
		basic['maskButton'] = maskButton
		basic['img2imgButton'] = img2imgButton

		# Denoise Strength
		slider = QSlider(Qt.Orientation.Horizontal, dialog)
		slider.setRange(0, 100)
		slider.setTickInterval(1)
		denoise_strength = slider
		labeldenoise_strength = QLabel(str(denoise_strength.value()/100))
		denoise_strength.valueChanged.connect(lambda: labeldenoise_strength.setText(str(denoise_strength.value()/100)))
		layoutH = QHBoxLayout()
		layoutH.addWidget(denoise_strength)
		layoutH.addWidget(labeldenoise_strength)
		container = QWidget()
		container.setLayout(layoutH)
		container.layout().setContentsMargins(0, 0, 0, 0)
		layout.addRow("Denoising", container)
		basic['denoise_strength'] = denoise_strength

		# Prompt Strength
		slider = QSlider(Qt.Orientation.Horizontal, dialog)
		slider.setRange(0, 80)
		slider.setTickInterval(1)
		cfg = slider
		cfg.setValue(28)
		labelPromptStrength = QLabel(str(cfg.value()/4))
		cfg.valueChanged.connect(lambda: labelPromptStrength.setText(str(cfg.value()/4)))
		layoutH = QHBoxLayout()
		layoutH.addWidget(cfg)
		layoutH.addWidget(labelPromptStrength)
		container = QWidget()
		container.setLayout(layoutH)
		container.layout().setContentsMargins(0, 0, 0, 0)
		layout.addRow("CFG", container)
		basic['CFG'] = cfg

		#multi size range slider
		SizeRange = range_slider.RangeSlider(Qt.Orientation.Horizontal, dialog)
		SizeRange.setRange(4, 32) #increments of 64
		SizeRange.setLow(8)
		SizeRange.setHigh(16)
		SizeRange.sliderMoved.connect(lambda: SizeRangeLabel.setText(str(SizeRange.low()*64) + " - " + str(SizeRange.high()*64)))
		layoutH = QHBoxLayout()
		layoutH.addWidget(SizeRange)
		SizeRangeLabel = QLabel(str(SizeRange.low()*64) + " - " + str(SizeRange.high()*64))
		layoutH.addWidget(SizeRangeLabel)
		container = QWidget()
		container.setLayout(layoutH)
		container.layout().setContentsMargins(0, 0, 0, 0)
		layout.addRow("Size Range", container)
		basic['SizeRange'] = SizeRange

		#HighResFix
		highResFix = QCheckBox()
		highResFix.setChecked(False)
		layout.addRow("High Resolution Fix",highResFix)
		basic['highResFix'] = highResFix

		# Seed
		seed = QLineEdit()
		layout.addRow("Seed (optional)", seed)
		basic['seed'] = seed

		# Model
		model = QComboBox()
		#get a list of models from the server
		models = hordeAPI.status_models()
		#add to combobox
		for Hordemodel in models:
			if Hordemodel["type"] == "image":
				model.addItem(Hordemodel["name"] + " (" + str(Hordemodel["count"]) + ")", Hordemodel["name"])
		model.setCurrentIndex(0)
		layout.addRow("Model", model)
		basic['model'] = model

		# sampler
		sampler = QComboBox()
		sampler_options = [ 'k_lms', 'k_heun', 'k_euler', 'k_euler_a', 'k_dpm_2', 'k_dpm_2_a', 'k_dpm_fast', 'k_dpm_adaptive', 'k_dpmpp_2s_a', 'k_dpmpp_2m', 'dpmsolver', 'k_dpmpp_sde', 'DDIM' ]
		for samplerchoice in sampler_options:
			sampler.addItem(samplerchoice)
		sampler.setCurrentIndex(3)
		layout.addRow("Sampler", sampler)
		basic['sampler'] = sampler
		
		# Steps
		slider = QSlider(Qt.Orientation.Horizontal, dialog)
		slider.setRange(10, 150)
		slider.setTickInterval(1)
		steps = slider
		labelSteps = QLabel(str(steps.value()))
		steps.valueChanged.connect(lambda: labelSteps.setText(str(steps.value())))
		layoutH = QHBoxLayout()
		layoutH.addWidget(steps)
		layoutH.addWidget(labelSteps)
		container = QWidget()
		container.setLayout(layoutH)
		container.layout().setContentsMargins(0, 0, 0, 20)
		layout.addRow("Steps", container)
		basic['steps'] = steps

		# Prompt
		prompt = QTextEdit()
		prompt.setAcceptRichText(False)
		layout.addRow("Prompt", prompt)
		basic['prompt'] = prompt

		# Negative Prompt
		negativePrompt = QTextEdit()
		negativePrompt.setAcceptRichText(False)
		layout.addRow("Negative Prompt", negativePrompt)
		basic['negativePrompt'] = negativePrompt

		#number of images
		numImages = QSpinBox()
		numImages.setRange(1, 30)
		numImages.setValue(1)
		layout.addRow("Number of Images", numImages)
		basic['numImages'] = numImages

		# Upscaler combobox
		upscale = QComboBox()
		upscale_options = ['None', 'RealESRGAN_x4plus', 'RealESRGAN_x2plus', 'RealESRGAN_x4plus_anime_6B', 'NMKD_Siax', '4x_AnimeSharp' ]
		for upscaler in upscale_options:
			upscale.addItem(upscaler)
		upscale.setCurrentIndex(0)
		layout.addRow("Upscaler", upscale)
		basic['upscale'] = upscale

		# Status
		statusDisplay = QTextEdit()
		statusDisplay.setReadOnly(True)
		layout.addRow("Status", statusDisplay)
		basic['statusDisplay'] = statusDisplay

		# Space
		layoutH = QHBoxLayout()
		layoutH.addSpacing(50)
		container = QWidget()
		container.setLayout(layoutH)
		layout.addWidget(container)

		# Cancel
		cancelButton = QPushButton("Cancel")
		cancelButton.setFixedWidth(100)
		layout.addWidget(cancelButton)
		layout.setAlignment(cancelButton, Qt.AlignRight)
		basic['cancelButton'] = cancelButton

		tabBasic.setLayout(layout)

		return tabBasic