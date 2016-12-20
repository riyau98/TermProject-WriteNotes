My term project is an application called Write Notes. It is an app that makes it easy to create, edit, and play back sheet music. Users can record their own audio, whether it be piano, singing, etc., and then have it converted to sheet music. Users first pick the clef and time signature they will be playing their audio in. Then they select the amount of time they would like to record and give their composition a title. Once finished recording, users can click the sheet music button to see their composition be written for them. Users can then play back their sheet music or continue to edit it by clicking notes and moving them up and down using the arrow keys.

The external python libraries used in this project were pyAudio and aubio. To download pyAudio, use the following commands (for Mac):
$brew install portaudio
$pip install pyadio
or visit https://people.csail.mit.edu/hubert/pyaudio/#downloads for more help.

It is best to download aubio for python2, as there is more documentation about this download. To download aubio, use:
$python -m pip install aubio
You can also install aubio using the following command(for Mac only):
$brew install aubio --with-python
For more installation help, visit https://aubio.org/download

To run this program, simply run finalTermProject.py