# VidGen

VidGen is a fun tool written with python that uses OpenAI to generate video scripts. It then fetches images from Google Images and other stock video sites and uses Google Cloud TTS to make *interesting* videos!

Try it out yourself!

## API Keys you will need

Review example_env_file for all the API keys you will need

## How To Generate A Video

1. If you are on a Mac you can double click on VidGen.command
2. If you are not on a mac, cd to the repo directory in your terminal and run "python gui.py"
3. After some set up (that you can monitor in terminal) a GUI will pop up.
4. Mix and match your video options
5. Once you are happy, hit Generate Resources
6. After the resources are done generating, review the generated files (script, images, etc)
7. If it all looks good, hit Create Movie to actually render the .mp4 file
8. Optional: For a more realistic voice experiment with using the google TTS options
