# Convert weaving pattern files to overshot-patterned double weave

The patterns must obey these restrictions (after optional filtering, and ignoring ends with no shaft and picks with no treadle):

* Each warp thread must be threaded on only one shaft.
* The pattern must contain treadling information (not pure liftplan).
* The pattern must use no more than one treadle per weft thread.
* The pattern must have the same number of treadles as shafts.

In addition, the ends and picks should change by a single shaft/treadle each step,
else the result will probably have floats that will mak the fabric unstable.

## Installing the Software

* Install [Python](https://www.python.org/downloads/) 3.11 or later.

* Install this "as_op_doubleweave" package on the computer with command: **pip install as_op_doubleweave**

## Usage

If your patterns do not yet obey the rules listed above, adjust them as needed.

To convert patterns to overshot-patterned doubleweave run:

  **as_op_doubleweave** ***pattern_files***

Filtering options:

  * **--skip-even-ends**  for shadow weave patterns, for example
  * **--skip-odd-ends**  (same)
  * **--skip-even-picks**  for shadow weave patterns, patterns with tabby added, etc.
  * **--skip-odd-picks**  (same)
  * **--skip-treadles** for patterns with dedicated treadles for tabby or other tie-down picks

Filtering can be used to remove tabby picks from overshot patterns (thus making the number of treadles and shafts match) and can also remove shadow picks from shadow weave.

The pattern files may be .wif or .dtx files.
The converted files are .wif files that are written to the same directory as the input files.Converted files include "as op doubleweave" in their name.

Also the converted files include a bit of program-specific information for
[WeaveIt](https://weaveit.com) that sets the weave type to double weave,
so the detailed fabric view looks correct.
Other programs will ignore this information.

### Pre-Filtering Patterns

You may find it helpful to filter a pattern first, then tweak the filtered pattern manually.
To do that, you can run command-line utility **filter_patterns**
with the same filtering options as **as_op_doubleweave**.

Filtered files include the filter options used in their name.

### Example

Here is an example using handweaving.net shadow weave pattern [79721](https://www.handweaving.net/draft-detail/79721/stars-and-diamonds-reena-meijer-drees-2004-2022).
First download the wif file (not as a liftplan), then proceed as follows:

You can remove the shadow ends and picks by filtering it. 
Skip even ends and odd picks results in a prettier pattern, in my opinion, and it avoids the need to fix colors in post-processing (if you skip all evens or all odds then ends and picks will all be the same color):

  **filter_patterns 79721.wif --skip-even-ends --skip-odd-picks**

This writes file "79721 skip-even-ends skip-even-picks.wif".

If you want to avoid bad floats, manually tweak the file to make ends and picks change by one shaft or treadle at a time.
Once you have done that, convert it:

  **as_op_doubleweave "79721 skip-even-ends skip-odd-picks.wif"**

This writes file "79721 skip-even-ends skip-odd-picks as op doubleweave.wif".

## Developer Tips

* Download the source code from [github](https://github.com/r-owen/as_op_doubleweave.git),
  or make a fork and download that.

* Inside the directory, issue the following commands:

    * **pip install -e .** (note the final period) to make an "editable installation" of the package.
      An editable installation runs from the source code, so changes you make to the source are used when you run or test the code, without the need to reinstall the package.

    * **pre-commit install** to activate the pre-commit hooks.
