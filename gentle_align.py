#file taken from gentle. Adapted to our needs

import argparse
import logging
import multiprocessing
import os
import sys
import gentle

nthreads=multiprocessing.cpu_count()
conservative = False
disfluency = False
log = 'INFO'

def on_progress(p):
        for k,v in p.items():
                logging.debug("%s: %s" % (k, v))  


def start_aligning(audiofile, txtfile, output):  
        log_level = "INFO" #can be one of the following: (DEBUG, INFO, WARNING, ERROR, or CRITICAL)
        logging.getLogger().setLevel(log_level)

        disfluencies = set(['uh', 'um'])
        
        with open(txtfile, encoding="utf-8") as fh:
                transcript = fh.read()

        resources = gentle.Resources()
        logging.info("converting audio to 8K sampled wav")

        with gentle.resampled(audiofile) as wavfile:
                logging.info("starting alignment")
                aligner = gentle.ForcedAligner(resources, transcript, nthreads)#, True, False, disfluencies)#, conservative, disfluencies)
                result = aligner.transcribe(wavfile, progress_cb=on_progress, logging=logging)

        fh = open(output, 'w', encoding="utf-8")
        fh.write(result.to_json(indent=2))
        logging.info("output written to %s" % (output))
