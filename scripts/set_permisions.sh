#!/bin/bash

direct=$1

chgrp -R wg-sierra-users $direct
chmod -R a+rX $direct

