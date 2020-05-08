#!/usr/bin/bash

cd "EXPChangeCriticWeight"
for f in *.sh
do
	dos2unix $f
	bsub < $f
done