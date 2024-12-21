Convert weaving pattern files to overshot-patterned double weave

Accepts .wif and .dtx pattern files.

Restrictions (after applying filters):

* Each warp thread must be threaded on only one shaft.
  (Technically, at most one shaft, because unthreaded warp threads are ignored.)
* The pattern must contain treadling information (not pure liftplan).
* The pattern must use no more than one treadle per weft thread.
* The pattern must have the same number of treadles as shafts.
