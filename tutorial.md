# Custom Cards with a Cutting Machine

Making your own custom card games is fun and rewarding!

You can play with your favorite artwork and designs. You can give cards to your friends and family. You can replace lost or damaged cards. 

In this tutorial, I'll show you how to make custom games with a cutting machine.

Why use a cutting machine though?

The alternative is to use a craft knife, a rotary cutter, or a paper guillotine and to do it all by hand. You can try your best but you're only human. Your cuts won't be exactly the same every time. Some cards will be too tall, too fat, slightly twisted, off center, or some combination of the above. Plus, you're body will be sore after the whole ordeal.

Join me in the 21st century where we have technology to solve our problems!

With the press of a button, a cutting machine will cut cards right before your eyes. Before it starts, it scans the page to calibrate itself, so each card comes out exactly the same, with rounded corners, perfectly sized, perfectly centered, the platonic ideal of a playing card.

Sounds like a dream? Keep reading!

## Disclaimer

In this tutorial, I'll show you the way I like to make cards, which is two-sided laminated card stock. I think it's great because they're durable, shuffle great, are dry erase, and need no sleeves.

However, maybe you already have a workflow you like! This tutorial still has value for you.

If you do any kind of manual cutting in your workflow, you can replace it with a cutting machine. For example, a common way to make custom cards is to slide a paper cutout in front of a sleeved, dummy card. Another way is to cut out a sticker to apply to a sacrificial card.

Any of these methods can be improved by using a cutting machine.

The goal here is, not necessarily convince you to follow my process, but show you how to use a cutting machine so you're empowered to use whatever method you want to make custom cards.

## Costs

Let's run the numbers.

Each sheet produces 8 cards and each sheet is composed of:
* a sheet of card stock, $10 for 150 sheets
* a lamination pouch, $20 for 200 pouches
* printer ink, $1 double-sided color printing

($10/150 sheets + $20/200 pouches) / 8 cards = $0.02 per card without printing

($10/150 sheets + $20/200 pouches + $1 printing) / 8 cards = $0.15 per card with double-sided printing

You could make a deck of 100 custom cards for around $15!

Sure, there may be a significant upfront cost to get started but you can quickly recoup the cost, especially if you're already accustomed to ordering custom cards online, paying for shipping, and sleeving up cards.

These businesses and they charge as much as $2 per card and $0.75 cents per card for bulk orders. That's a farcry from $0.15 per card!

The most expensive purchase you'll likely make is the cutting machine, which can cost $300.

However, if you were considering ordering custom cards but decided to make them instead, you could recoup the cost of the printer in as few as 165 cards and as many as 500 cards, given the aforementioned pricing. To some, that may sound like a lot of cards, but to others, that's negligible.

And if you're already a card-making aficionado, perhaps you wouldn't save much monetarily but if you're doing the work manually, you'd save time and wear on your body if you used a cutting machine. Perhaps, that's worth it in and of itself.

## Tools

Equipment
* Cutting machine
* Thermal laminator
* Printer
* Computer

I recommend using the Silhouette Cameo 5 because it's the cutting machine I use. There are many other cutting machines that could potentially get the job done but because the scripts and templates provided in this tutorial are for Silhouette suite of software and devices, I recommend getting this machine.

However, if the upfront cost is too high, you can also consider purchasing a Cameo 4, which is the previous generation. At the moment, the Cameo 4 is discontinued but the Cameo 4 Plus is still available and is significantly cheaper than the Cameo 5. The Cameo 4 shares many of the same features as the Cameo 5, including Print & Cut, which is the most important feature for making custom cards.

Materials
* Printer ink
* Card stock (60 lb)
* Thermal lamination sheets (3 mil)

The card stock I use is 110 lb but some home printers cannot handle it. For that reason, I am recommending 60 lb card stock but feel free to experiment.

Optional
* Hobby knife
* Extra cutter blades (AutoBlade)
* Extra cutter mats

You might want a hobby knife because sometimes, you'll the cutting machine will leave you a straggler card where it's not completely detached. You can use the hobby knife to finish the cut.

For the purposes of cutting cards, your cutter blades should last a long time. However, if you're new to using these machines, you could accidentally break the blade due to improper configuration or set up. Consider buying an extra one as a back up. For the Cameo 5, buy the standard AutoBlade.

You'll definitely want to pick up extra cutting mats however. Cutting mats are sticky so they hold the paper as its being cut. Over time, they'll lose their stickiness. You'll want to have replacements ready but each cutting mat should last you a few hundred cards.

## Primer on Cutting Machines

The cutting machine is core to this process so it's important to give some background on how they work so you'll be better prepared to operate one.

### Silhouette Cameo 5

The Cameo 5 is an electronically operated cutting machine. It's similar to a laser cutter or a CNC machine. A computer controls the movement of the toolhead, which contains a small blade similar to a hobby knife, and the toolhead will cut the material. You can control various cutting parameters including the speed of the blade and the pressure of the blade, and you can cut various materials including paper, card stock, sticker paper, cardboard, vinyl, foam, fabric, and even leather. You can also purchase special add-on tools for foiling, embossing, and other purposes.

Additionally, the Cameo 5 supports Print & Cut. Print & Cut means the machine scans your printed page and automatically adjusts itself so that it's able to cut precisely and consistently every time. You do not have to worry about aligning the paper for cutting as the machine will make adjustments as needed. As long as the paper is generally in the right area, the machine can compensate for placement and tilt. This is pivotal for card games because you want the backs of every card to be indistinguishable. More on Print & Cut later.

### Silhouette Studio

Silhouette Studio is the software used to create cutting designs and control the Cameo 5. It is easy to use and has simple visual UI. You can create a cutting template by drawing shapes on then screen and when you are ready, the machine will cut those shapes out. You can do fancier things like import an image (with a transparent background) and the software can cut out its outline, which is great for stickers and collages. However, I've included cutting templates in this tutorial so you won't need to make your own unless you're interested in making cards in a special size or shape.

As mentioned before, an important aspect of this process is Print & Cut. You need to enable it in a cutting template in order to reap the benefits. When you enable Print & Cut, Silhouette Studio will do two things, it'll add registration marks to your cutting template, and when you print, it'll have the machine scan for registration marks before cutting. The registration marks are what the cutting machine uses to determine the orientation of your paper and make the proper adjustments when cutting. However, the templates in this tutorial already have Print & Cut enabled so you will not need to change anything.

## Prerequisites

### Printer alignment

If you plan on having card backs and/or if you plan on making double faced cards, then you need to ensure that printer can print with good front and back alignment. Otherwise, your card fronts and backs may have an offset.

Your printer may have built-in tools for calibration and alignment adjustment. However, if you do not have access to your printer's settings, I have provided a CLI tool that can add an offset to every other page in a provided PDF. You can use this offset to compensate to offset that your printer naturally provides. To learn more, see [here](README.md#offset_pdfpy).

### Cutting settings

Silhouette Studio provides a number of cutting settings, including blade pressure, cutting speed, passes, and blade depth.

Before starting the tutorial, determine the cutting settings that works best for you and the materials you want to cut.

Unfortunately, there are no short cuts for this. You will need to do some experimentation on your own.

I recommend creating a simple cutting template with Silhouette Studio. Set the blade pressure, cutting speed, and blade depth to something reasonable, but set passes to 1. You can have the machine recut again and again to determine the required passes. Prepare your cutting material, stick the material onto the cutting mat, insert the mat into the machine, and start the cutting job. Try different combinations of settings and repeat as necessary.

The following is a table of working settings from various testers. Do not use these settings blindly. Test conservatively and work up to the listed values. If not, you risk breaking your machine or cutting through your mat.

| Machine | Blade          | Card stock     | Lamination | Pressure | Speed | Passes | Depth |
| ------- | -------------- | -------------- | ---------- | -------- | ----- | ------ | ----- |
| Cameo 5 | Autoblade      | 65 lb          | 3 mil      | 30       | 30    | 3      | 7     |
| Cameo 5 | Autoblade      | 110 lb         | 3 mil      | 33       | 20    | 3      | 7     |
| Cameo 5 | Autoblade      | 110 lb/199 gsm | 3 mil      | 33       | 30    | 4      | 10    |
| Cameo 3 | Deep-Cut Blade | 110 lb         | 3 mil      | 33       | 5     | 5      | 19    |

## Instructions

### Set up environment

[Install Silhouette Studio](https://www.silhouetteamerica.com/silhouette-studio).

[Install Python](https://www.python.org/downloads/).

[Install Git](https://github.com/git-guides/install-git).

Clone this repo.

```shell
git clone git@github.com:Alan-Cha/silhouette-card-maker-testing.git
```

Open the repo.
```shell
cd silhouette-card-maker-testing
```

Create a Python virtual environment.
```shell
python -m venv venv
```

Activate the Python virtual environment.
```shell
. venv/bin/activate
```

Download Python packages.
```shell
pip install -r requirements.txt
```

### Create the PDF

First, collect all the card front images and put them into `game/front`. Then, put a card back image into `game/back`.

My friend Jon Lenchner, who designed the game Zero sumZ, has offered his game as an example for this tutorial. Zero sumZ is a abstract set collection game and you can find the game assets, including the front images, the back image, and instructions [here](examples/ZERO%20SUMZ/).

Generate the PDF with the following:

```shell
python create_pdf.py
```

You can find the PDF in `game/output/game.pdf`.

### Prepare the sheets

Print out the PDF and laminate the sheets.

Because cardstock is thicker than normal printer paper, you may need to set your laminator at a higher setting in order to get good lamination. If not, you may have cloudy lamination and delamination issues.

### Cut the sheets

As mentioned previously, there are a number of different cutting templates. Open the appropriate one in Silhouette Studio and configure the cutting settings.

Put a laminated sheet on the cutting mat. The side with the registration marks, the black square and "L"s, should face up. Orient the sheet so that the black square is in the top left corner. Apply the laminated sheet onto the mat such that the top left corner of the card stock, not the lamination, is aligned with the top left corner of the grid on the mat.

Insert the mat into the machine. The left edge of the mat should be aligned with the notch on the machine. Then, click the media load button on the machine.

Finally, start the cutting job. The machine should begin the Print & Cut process and cut out the cards.

### Finish the cards

Click the media eject button on the machine to remove the mat. Pull off the cards and excess.

Because the cutting process may cause the card edges to delaminate, put the cards through the laminator a second time.

Now you're ready to play with your cards!

## Contributing

## FAQ

### Do I need to laminate my cards?

No. Lamination provides a lot of advantages like durability, water resistance, shuffleability, and card feel, but it's not necessary. However, if you're planning on using a cutting machine to help with another workflow that doesn't require lamination, you don't need to do so.

### How do laminated cards compared to mass produced cards?

It depends on the weight of your card stock and the thickness of your lamination, but from personal experience with 110 lb card stock and 3 mil lamination, I think it's very similar to mass produced cards.

If I had to say anything, I would say this combination is only marginally thicker than mass produced card but if you plan on using card sleeves and playing with a mix of both, I would say it's almost indistinguishable.

### Can I make double-sided cards?

Yes. The `create_pdf.py` script has many other features including laying out double-sided cards. To see the full documentation, please see [here](README.md#double-sided-cards).

Long story short, put the fronts in `game/front` and the backs in `game/double_sided`. The names of the files must match for each pair. Then, simply run `create_pdf.py` as usual.

### Do you have printer recommendations?

No, but I can give you give you some ideas on what you should look for.

First, I do not recommend getting a laser printer. The laser toner affects the lamination, causing it to easily delaminate. It can work, but you may have issues with delamination during cutting and while removing cards from the cutting mat.

Secondly, determine what kind of custom cards you'd like to make. Do you want to make double-sided laminated cardstock cards like mine? Perhaps single sided is suitable for your situation? Perhaps you'd like to cut out regular printer paper or sticker paper and use an alternative way of making custom cards.

Not all printers can handle card stock, and even if it can handle card stock, it may not be able to handle thicker card stock like 110 lb. Additionally, if you plan on making double-sided cards, getting a printer that can do duplex printing would be ideal. If you have a simplex printer, you can feed the printed pages back into printer to achieve double-sided printing, but you could have issues with alignment.

Invest in a good printer because you want the cards to look nice as you play with them and because poor quality printing can also affect the Cameo's Print & Play.

### My are my card delaminating?

Are you using a laser printer? The laser toner sticks to the lamination, which prevents the lamination from sticking to the paper. Laser printing can work with this process, but you'll have to be gentler with the cards while cutting and while playing.

Try laminating a second time or laminating at a higher setting before cutting. Because card stock is thicker than printer paper, you need to use more heat to get proper lamination. Additionally, this will help to clear up any cloudiness in your lamination, making your cards look better in the end.

### Why are my cards wavy?

Set your laminator to a lower setting. It's adding too much heat, causing the lamination to contract more than needed.

Alternatively, immediately put the laminated sheets under a heavy book to let them cool down flat.

### Why is the registration failing?

Ensure that there is nothing blocking the registration sensor.

Ensure that the sheets are generated with the right template and printed with 100% scale.

Ensure the sheet is placed correctly on the mat and the mat is placed correctly in the machine. Otherwise, the machine can struggle to scan the registration marks. The top left corner of the paper, not the lamination, should align with the top left corner of the grid on the mat. The left edge of the mat should align with the notch on the machine.

The registration process is the following: first the scan the black square in the top left, then the L in the bottom left, and finally the L in the top right. In my own experience, the registration can occasionally fail as the machine is scanning the bottom left L. This occurs when the machine accidentally scans the bottom left card as it's searching for the bottom left L. If you have this issue, a workaround is to cover the bottom left card with a Post-It note during registration and removing it before cutting.

If none of the previous tips worked, the issue may be your choice of paper, lamination, and printing. If you are using a low quality printer and the registration marks are not dark enough, the registration can fail.

### Why is my machine cutting in the wrong place?

Make sure you're using the right cutting template. Each sheet should be labeled with the cutting template it's associated with, for example "letter_bridge_v1".

### Why are my cards offset?

If either the fronts or the backs are offset, then there's most likely an issue with your printer alignment. Refer to your printer's instruction manual and try to recalibrate it. If there's no way to change the printer's settings, try using [offset.py](README.md#offset_pdfpy) to compensate for the offset.

If both the fronts and backs are offset, then there may be an issue with registraion. Ensure that you are printing with the right scale and cutting with the right cutting template, and ensure that there's nothing that can interfere with the registration process.

## Special thanks