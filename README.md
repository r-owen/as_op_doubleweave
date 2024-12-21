# Convert weaving pattern files to overshot-patterned double weave

The patterns must obey these restrictions (after optional filtering):

* Each warp thread must be threaded on only one shaft.
  (Technically, at most one shaft, because unthreaded warp threads are ignored.)
* The pattern must contain treadling information (not pure liftplan).
* The pattern must use no more than one treadle per weft thread.
* The pattern must have the same number of treadles as shafts.

## Installing the Software

* Install [Python](https://www.python.org/downloads/) 3.11 or later.

* Install this "as_op_doubleweave" package on the computer with command: **pip install as_op_doubleweave**

## Usage

On the command line run:

  **as_op_doubleweave** ***pattern_files***

The pattern files may be .wif or .dtx files. The converted files are always .wif.

Filtering options:

  * **--skip-even-ends**  for shadow weave patterns, for example
  * **--skip-odd-ends**  (same)
  * **--skip-even-picks**  for shadow weave patterns, patterns with tabby added, etc.
  * **--skip-odd-picks**  (same)
  * **--skip-treadles** for patterns with dedicated treadles for tabby or other tie-down picks

Here is an example using handweaving.net shadow weave pattern 79721. First download the wif file, then convert it as follows:

  **as_op_doubleweave 79721.wif --skip-even-ends --skip-even-picks**

You can also include all ends and picks from the original pattern. This gives nice, but very different, result:

  **as_op_doubleweave 79721.wif**

## Developer Tips

* Download the source code from [github](https://github.com/r-owen/as_op_doubleweave.git),
  or make a fork and download that.

* Inside the directory, issue the following commands:

    * **pip install -e .** (note the final period) to install an "editable" version of the package.
      Meaning a version that runs from the source code, so any changes you make can be run without reinstalling.

    * **pre-commit install** to activate the pre-commit hooks.
