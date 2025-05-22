---
title: 'Cutting Guide'
weight: 20
---

## Prerequisites

### Printer alignment

If you plan on having card backs and if you plan on making double faced cards, then you need to ensure that printer can print with good front and back alignment. Otherwise, your card fronts and backs may have an offset.

Your printer may have built-in tools for calibration and alignment adjustment. However, it doesn't, you can use [`offset_pdf.py`]({{% ref "../docs/offset.md" %}}) to compensate for the printer's offset.

### Cutting settings

Silhouette Studio provides a number of cutting settings, including **blade force**, **cutting speed**, **passes**, and **blade depth**.

<!-- !TODO: screenshot of Silhouette Studio cutting settings -->

Before starting, determine the cutting settings that works best for you and the materials you want to cut.

To do this, first create a simple cutting template in Silhouette Studio. Then, set the blade force, cutting speed, and blade depth to something reasonable, but set passes to 1. You can have the machine recut again and again to determine the required passes. Change the settings as necessary.

<!-- !TODO: screenshot of a simple cutting template -->

The following is a table of working settings from various testers. Do not use these settings blindly. Test conservatively. If not, you risk breaking your machine or cutting through your mat.

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

Before starting, I recommend joining our [Discord server](https://discord.gg/jhsKmAgbXc). If you have any questions, feel free to ask them in the `troubleshooting` channel.

### Set up environment

[Install Silhouette Studio](https://www.silhouetteamerica.com/silhouette-studio).

Download the code by cloning the repo or clicking [here](https://github.com/Alan-Cha/silhouette-card-maker-testing/archive/refs/heads/main.zip). Unzip the code if necessary.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

### Check if Python is installed
```shell
python --version
```

If the command is not recognized, you can also try:
```shell
python3 --version
```

If you don't have Python, install it [here](https://www.python.org/downloads/). Check the box to **"Add Python to PATH"** if asked. After installation, close **Terminal**/**PowerShell** and open a new instance.

### Upgrade pip

```shell
python -m pip install --upgrade pip
```

### Navigate to the code

```shell
cd <path to the code>
```

> [!NOTE]
> If you downloaded the code in the `Downloads` folder, then use the following:
> ```shell
> cd Downloads/silhouette-card-maker-testing-main/silhouette-card-maker-testing-main
> ```

### Create a virtual environment

```shell
python -m venv venv
```

Then, activate the environment:

{{< tabs items="macOS/Linux,Windows" defaultIndex="1" >}}

  {{< tab >}}
```shell
. venv/bin/activate
```
  {{< /tab >}}
  {{< tab >}}
```powershell
.\venv\Scripts\Activate.ps1
```

> [!NOTE]
> If you see a **security error**, run the following, then try activating the environment again.
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```
  {{< /tab >}}

{{< /tabs >}}

### Install Python packages

```shell
pip install -r requirements.txt
```

### Create the PDF

Put card front images into `game/front`. Then, put a card back image into `game/back`.

> [!TIP]
> I've prepared the game, Zero sumZ, as an [example](https://github.com/Alan-Cha/silhouette-card-maker-testing/tree/main/examples/ZERO%20SUMZ). Simply move the assets to the appropriate image folders.
>
> You can also use a [plugin]({{% ref "../plugins" %}}) to populate the image folders. For example, the [Magic: The Gathering plugin]({{% ref "../plugins/mtg.md" %}}) reads a decklist and automatically fetches card art.

Generate the PDF with the following:

```shell
python create_pdf.py
```

> [!TIP]
> `create_pdf.py` offers many options such as configuring paper and card size, supporting double-sided cards, and adding registration marks to the front sides. To learn more, see [here]({{% ref "../docs/create.md" %}}).

You can find the PDF in `game/output/game.pdf`.

### Prepare the sheets

Print out the PDF and laminate the sheets.

> [!TIP]
> Because cardstock is thick, you may need to use a higher setting on your laminator. If not, you may have cloudy lamination and delamination issues.

### Cut the sheets

Open the `letter_standard_<version>.studio3` cutting template in Silhouette Studio. Cutting templates can be found in the [`cutting_templates`](https://github.com/Alan-Cha/silhouette-card-maker-testing/tree/main/cutting_templates) directory.

Put a laminated sheet on the cutting mat. The side with the registration marks, the black square and "L"s, should face up. Orient the sheet so that the black square is in the top left corner. Apply the laminated sheet onto the mat such that the top left corner of the card stock, not the lamination, is aligned with the top left corner of the grid on the mat.

![Sheet alignment](/images/sheet_alignment.jpg)

Insert the mat into the machine. The left edge of the mat should be aligned with the notch on the machine. Then, click the media load button on the machine.

![Mat alignment](/images/mat_alignment.jpg)

Finally, start the cutting job.

### Finish the cards

Click the media eject button on the machine to remove the mat.

Peel off the cards and remove the excess.

Because the cutting process may cause the card edges to delaminate, put the cards through the laminator a second time.

![Relaminating the cards.](/images/relamination.jpg)

Now you're ready to play with your cards!

## Next Steps

As mentioned, the `create_pdf.py` script offers many [configuration options]({{% ref "../docs/create.md" %}}). `create_pdf.py` can create double-sided cards, utilize different paper sizes, cut different card sizes, and more!

If you're interested in making proxies for TCGs, try using a [plugin]({{% ref "../plugins" %}}). For example, the [Magic: The Gathering plugin]({{% ref "../plugins/mtg.md" %}}) reads a decklist and automatically fetches card art.

Lastly, we have a [Discord server](https://discord.gg/jhsKmAgbXc)! We'd love to see you there! You can ask for help, share pictures, and chat with people who all love creating and playing card games.

Thanks for reading and best of luck with your card cutting adventures!