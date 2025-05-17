---
title: 'Cutting Guide'
weight: 20
---

## Prerequisites

### Printer alignment

If you plan on having card backs and/or if you plan on making double faced cards, then you need to ensure that printer can print with good front and back alignment. Otherwise, your card fronts and backs may have an offset.

Your printer may have built-in tools for calibration and alignment adjustment. However, if you do not have access to your printer's settings, I have provided a CLI tool that can add an offset to every other page in a provided PDF. You can use this offset to compensate to offset that your printer naturally provides. To learn more, see [here](README.md#offset_pdfpy).

### Cutting settings

Silhouette Studio provides a number of cutting settings, including blade force, cutting speed, passes, and blade depth.

<!-- !TODO: screenshot of Silhouette Studio cutting settings -->

Before starting the tutorial, determine the cutting settings that works best for you and the materials you want to cut.

Unfortunately, there are no short cuts for this. You will need to do some experimentation on your own.

I recommend creating a simple cutting template with Silhouette Studio. Set the blade force, cutting speed, and blade depth to something reasonable, but set passes to 1. You can have the machine recut again and again to determine the required passes. Prepare your cutting material, stick the material onto the cutting mat, insert the mat into the machine, and start the cutting job. Try different combinations of settings and repeat as necessary.

<!-- !TODO: screenshot of a simple cutting template -->

The following is a table of working settings from various testers. Do not use these settings blindly. Test conservatively and work up to the listed values. If not, you risk breaking your machine or cutting through your mat.

| Machine      | Blade          | Card stock     | Lamination  | Force    | Speed | Passes | Depth |
| ------------ | -------------- | -------------- | ----------- | -------- | ----- | ------ | ----- |
| Cameo 5      | Autoblade      | 65 lb          | 3 mil       | 30       | 30    | 3      | 7     |
| Cameo 5      | Autoblade      | 65 lbs/250 gsm | 3 mil       | 30       | 20    | 4      | 7     |
| Cameo 5      | Autoblade      | 110 lb         | 3 mil       | 33       | 20    | 3      | 8     |
| Cameo 5      | Autoblade      | 110 lb/199 gsm | 3 mil       | 33       | 30    | 4      | 10    |
| Cameo 5      | Autoblade      | 220 gsm        | 150 microns | 30       | 26    | 4      | 8     |
| Cameo 5      | Autoblade      | 250 gsm        | 120 microns | 40       | 10    | 8      | 10    |
| Cameo 4 Plus | Autoblade      | 110 lb         | 3 mil       | 30       | 30    | 3      | 5     |
| Cameo 3      | Deep-Cut Blade | 110 lb         | 3 mil       | 33       | 5     | 5      | 19    |

## Instructions

### Set up environment

[Install Silhouette Studio](https://www.silhouetteamerica.com/silhouette-studio).

Git clone this repo. If you don't know how, you can download the code [here](https://github.com/Alan-Cha/silhouette-card-maker-testing/archive/refs/heads/main.zip). Then unzip the code.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

---

### Navigate to the code

If you cloned the repo, you know what to do.

If you don't, then you need to determine the path to your unzipped code is.

For example, if you unzipped it in your `Downloads` folder, then the following command will navigate you to the code.

```shell
cd Downloads/silhouette-card-maker-testing-main/silhouette-card-maker-testing-main
```

---

### Check if Python is installed
```shell
python --version
```

If you don't have Python, install it [here](https://www.python.org/downloads/). Be sure to check the box **"Add Python to PATH"** during installation.

---

### Upgrade pip (Python's package manager)
```shell
python -m pip install --upgrade pip
```

---

### Create and activate a Python virtual environment

Create the virtual environment:
```shell
python -m venv venv
```

Activate the environment:

{{< tabs items="macOS/Linux,Windows" defaultIndex="1" >}}

  {{< tab >}}
**Terminal (macOS/Linux):**
```shell
. venv/bin/activate
```
  {{< /tab >}}
  {{< tab >}}
**PowerShell (Windows):**
```powershell
.\venv\Scripts\Activate.ps1
```

> [!NOTE]
> You may see a **security error**. If you do, run the following, then try activating the environment again.
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```
  {{< /tab >}}

{{< /tabs >}}

---

### Install Python packages
```shell
pip install -r requirements.txt
```

---

### Create the PDF

First, put all your card front images into `game/front`. Then, put a card back image into `game/back`.

> [!NOTE]
> My friend, Jon Lenchner, has offered his card game, Zero sumZ, as an example for this tutorial. Zero sumZ is a abstract pattern-matching game and you can find the game assets [here](https://github.com/Alan-Cha/silhouette-card-maker-testing/tree/main/examples/ZERO%20SUMZ). These game assets are for educational purposes only.

Generate the PDF with the following:

```shell
python create_pdf.py
```

You can find the PDF in `game/output/game.pdf`.

> [!TIP]
> `create_pdf.py` offers many options such as configuring paper and card size, supporting double-sided cards, and adding registration marks to the front sides. To learn more, see [here]({{% relref "../docs/create.md" %}}).

---

### Prepare the sheets

Print out the PDF and laminate the sheets.

> [!TIP]
> Because cardstock is thicker than normal printer paper, you may need to set your laminator at a higher setting in order to get good lamination. If not, you may have cloudy lamination and delamination issues.

---

### Cut the sheets

Open the `letter_standard_<version>.studio3` cutting template in Silhouette Studio. Cutting templates can be found in the [`cutting_templates`](https://github.com/Alan-Cha/silhouette-card-maker-testing/tree/main/cutting_templates) directory.

<!-- > [!NOTE]
> The cutting template you should use depends on your PDF generation options. -->

Put a laminated sheet on the cutting mat. The side with the registration marks, the black square and "L"s, should face up. Orient the sheet so that the black square is in the top left corner. Apply the laminated sheet onto the mat such that the top left corner of the card stock, not the lamination, is aligned with the top left corner of the grid on the mat.

![Sheet alignment](/images/sheet_alignment.jpg)

Insert the mat into the machine. The left edge of the mat should be aligned with the notch on the machine. Then, click the media load button on the machine.

![Mat alignment](/images/mat_alignment.jpg)

Finally, start the cutting job. The machine should begin the Print & Cut process and cut out the cards.

---

### Finish the cards

Click the media eject button on the machine to remove the mat. Peel off the cards and excess.

Because the cutting process may cause the card edges to delaminate, put the cards through the laminator a second time.

![Relaminating the cards.](/images/relamination.jpg)

Now you're ready to play with your cards!

## Next Steps

As mentioned, the `create_pdf.py` script offers many configuration options. Try exploring some of these options to determining what works best for you. For example, a common use case is to only print the card fronts to save on ink. By default, the PDF generation puts the registration on the card backs, because if you play unsleeved, it's important for the card backs to be consistent. However, if you want to override this behavior, you can use the `--only_fronts` option. `create_pdf.py` can also create double-sided cards, utilize different card and paper sizes, and more! See [here]({{% relref "../docs/create.md" %}}) for more information.

In regards to rerunning `create_pdf.py` in the future, you only need to do a few steps. Simply open Terminal or Powershell, navigate to the code, activate the virtual environment, and run `create_pdf.py`. You do not need to recreate the virtual environment or reinstall Python packages. However, this project will continue to grow and offer new features. If you want to get the latest updates, then you would have to get the latest code, create a new virtual environment, and reinstall Python packages.

Lastly, we have a [Discord server](https://discord.gg/jhsKmAgbXc)! We'd love to see you there! You can find help if you're struggling with the tutorial, you can see pictures of other people's cards, and you talk to many different people who are all interested in creating board games and playing card games.

Thanks for reading and best of luck with your card cutting adventures!