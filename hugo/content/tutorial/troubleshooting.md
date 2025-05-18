---
title: 'Troubleshooting'
weight: 1000
---

## Do I need to laminate my cards?

No. Lamination provides a lot of advantages like durability, water resistance, shuffleability, and card feel, but it's not necessary. However, if you're planning on using a cutting machine to help with another workflow that doesn't require lamination, you don't need to do so.

## Are laminated cards similar to mass produced cards?

It depends on the weight of your card stock and the thickness of your lamination, but from personal experience with 110 lb card stock and 3 mil lamination, I think it's very similar to mass produced cards.

If I had to say anything, I would say this combination is only marginally thicker than mass produced card but if you plan on using card sleeves and playing with a mix of both, I would say it's almost indistinguishable.

## Can I make double-sided cards?

Yes, the `create_pdf.py` script has many other features including laying out double-sided cards. To see the full documentation, please see [here]({{% ref "../docs/create.md#double-sided-cards" %}}).

Long story short, put the fronts in `game/front` and the backs in `game/double_sided`. The names of the files must match for each pair. Then, simply run `create_pdf.py` as usual.

## Do you have printer recommendations?

No, but I can give you give you some ideas on what you should look for.

First, I do not recommend getting a laser printer. The laser toner affects the lamination, causing it to easily delaminate. It can work, but you may have issues with delamination during cutting and while removing cards from the cutting mat.

Secondly, determine what kind of custom cards you'd like to make. Do you want to make double-sided laminated cardstock cards like mine? Perhaps single sided is suitable for your situation? Perhaps you'd like to cut out regular printer paper or sticker paper and use an alternative way of making custom cards.

Not all printers can handle card stock, and even if it can handle card stock, it may not be able to handle thicker card stock like 110 lb. Additionally, if you plan on making double-sided cards, getting a printer that can do duplex printing would be ideal. If you have a simplex printer, you can feed the printed pages back into printer to achieve double-sided printing, but you could have issues with alignment.

Invest in a good printer because you want the cards to look nice as you play with them and because poor quality printing can also affect the Cameo's Print & Play.

## Why are my card delaminating?

Are you using a laser printer? The laser toner sticks to the lamination, which prevents the lamination from sticking to the paper. Laser printing can work with this process, but you'll have to be gentler with the cards while cutting and while playing.

Try laminating a second time or laminating at a higher setting before cutting. Because card stock is thicker than printer paper, you need to use more heat to get proper lamination. Additionally, this will help to clear up any cloudiness in your lamination, making your cards look better in the end.

## Why are my cards wavy?

Set your laminator to a lower setting. It's adding too much heat, causing the lamination to contract more than needed.

Alternatively, immediately put the laminated sheets under a heavy book to let them cool down flat.

## Why is the registration failing?

Ensure that there is nothing blocking the registration sensor.

Ensure that the sheets are generated with the right template and printed with 100% scale.

Ensure the sheet is placed correctly on the mat and the mat is placed correctly in the machine. Otherwise, the machine can struggle to scan the registration marks. The top left corner of the paper, not the lamination, should align with the top left corner of the grid on the mat. The left edge of the mat should align with the notch on the machine.

Try playing around with the lighting. If the room is too bright or too dark, the machine may have issues. Try shining a light at the sensor to provide more lighting. Try closing the cover as well.

In my own experience, the registration can occasionally fail as the machine is scanning the bottom left L. This occurs when the machine unintentionally scans the bottom left card as it's searching for the bottom left L. If you have this issue, try covering the bottom left card with a Post-It note during registration and removing it before cutting.

![Registration fix](/images/registration_fix.jpg)

If none of the previous tips worked, the issue may be your choice of paper, lamination, or printing.

## Why didn't my machine cut all the way through?

Did you configure your cutting settings? The cutting templates do not contain cutting settings. You must add your settings manually. To learn more, see [here]({{% relref "guide.md#cutting-settings" %}}). 

If you configured you cutting settings, then try adjusting your settings by adding more force or more passes. If you are still having issues, try using a new blade and/or mat.

## Why is my machine cutting in the wrong place?

Make sure you're using the right cutting template. Each sheet should be labeled with the cutting template it's associated with, for example "letter_bridge_v1".

## Why did my cards come out diagonally?

As mentioned in [Why is the registration failing?](#why-is-the-registration-failing), your machine may occasionally scan the bottom left card as it's searching for the bottom left L during registration. When this happens, the machine may either stop and complain, or continue and start cutting cards diagonally. To fix this, try being more careful when you place the sheet and the mat, or employ the Post-It note trick.

## Why are my cards offset?

If either the fronts or the backs are offset, then there's most likely an issue with your printer alignment. Refer to your printer's instruction manual and try to recalibrate it. If there's no way to change the printer's settings, try using [offset.py]({{% ref "../docs/offset.md" %}}) to compensate for the offset.

If both the fronts and backs are offset, then there may be an issue with registraion. Ensure that you are printing with the right scale and cutting with the right cutting template, and ensure that there's nothing that can interfere with the registration process.

## Why are my cards the wrong size?

Some printers secretly add an offset to your prints, even if they are set to 100% scale or actual size. You may need to do some manual calibration in order to have your cards print and be cut out at the right size.