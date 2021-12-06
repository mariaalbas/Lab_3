import subprocess
import json


# We create the class ffmpeg() with all the requested methods
def ffmpeg():
    # This method outputs the macroblocks and motion vectors of BBB_cut.mp4
    def mb_and_mv(input):
        # We extract the macroblocks from the cut version of BBB.mp4 using the following FFMpeg command line
        subprocess.call(['ffmpeg', '-debug', 'mb_type', '-i', str(input), 'BBB_macroblocks.mp4', '2>', 'macroblocks.txt'])
        # We also extract the motion vectors using the following FFMpeg command line
        subprocess.call(['ffmpeg', '-flags2', '+export_mvs', '-i', str(input),
                         '-vf', 'codecview=mv=pf+bf+bb', 'BBB_motionvectors.mp4'])

    # This method creates a new BBB container by following the necessary steps
    def BBB_container(input):
        # We cut BBB.mp4 into a 1 minute video for further computations
        subprocess.call(['ffmpeg', '-ss',  '00:00:00', '-i', str(input), '-c', 'copy', '-t', '00:01:00', 'BBB_1min.mp4'])
        # We cut BBB.mp4 into a 1 minute video without audio
        subprocess.call(['ffmpeg', '-ss',  '00:00:00', '-i', str(input), '-c', 'copy', '-t', '00:01:00', '-an', 'BBB_1min_noaudio.mp4'])
        # We export the 1 minute version audio as MP3 stereo track
        subprocess.call(['ffmpeg', '-i', 'BBB_1min.mp4', '-c:a', 'libmp3lame', 'BBB_in_mp3.mp3'])
        # We export the 1 minute version audio as AAC with lower bitrate
        subprocess.call(['ffmpeg', '-i', 'BBB_1min.mp4', '-c:a', 'aac', '-b:a', '64k', 'BBB_in_AAC.aac'])
        # We package everything as .mp4 in a new version named BBB_container.mp4
        subprocess.call(['ffmpeg', '-i', 'BBB_1min.mp4', '-i', 'BBB_in_mp3.mp3', '-i', 'BBB_in_AAC.aac', '-c:v', 'copy',
                         '-c:a', 'copy', '-map', '0:0', '-map', '1:a', '-map', '2:a', 'BBB_container.mp4'])

    # This method assigns a broadcasting standard to each video and audio format of the container
    def broadcasting(input):
        # We save in the variable 'data' the tracks of the mp4 container in a json format
        d = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', str(input)], capture_output=True).stdout
        data = json.loads(d)
        # We read the codec names for both video and audio and store them in two separate lists
        h264 = data['streams'][0]['codec_name']
        mp3 = data['streams'][1]['codec_name']
        aac = data['streams'][2]['codec_name']
        video = [h264]
        audio = [mp3, aac]
        # We iterate the two lists and print which broadcasting standards would fit for all possible combinations
        if ('h264' in video) or ('mpeg2' in video) and ('mp3' in audio) or ('aac' in audio):
            print('The broadcasting standards can be DVB, ISDB or DTMB.')
        elif ('h264' in video) or ('mpeg2' in video) and ('ac-3' in audio):
            print('The broadcasting standards can be DVB, ATSC or DTMB.')
        elif ('h264' in video) or ('mpeg2' in video) or ('avs' in video) or ('avs+' in video) and ('aac' in audio) \
                or ('dra' in audio) or ('ac-3' in audio) or ('mp2' in audio) or ('mp3' in audio):
            print('The broadcasting standard is DTMB.')

    # This method integrates subtitles to the video and creates a new version named BBB_subtitled.mp4
    def add_subtitles(input, subtitles):
        # We resize the BBB.mp4 video, conserving its aspect ratio, no fit the subtitles
        subprocess.call(['ffmpeg', '-i', str(input), '-vf', 'scale=320:-1', 'BBB_320.mp4'])
        # We add the subtitles to the video
        subprocess.call(['ffmpeg', '-i', 'BBB_320.mp4', '-vf', str(subtitles), 'BBB_subtitled.mp4'])

    # We initialize the necessary variables
    video = 'BBB.mp4'
    cut = 'BBB_cut.mp4'
    container = 'BBB_container.mp4'
    bbb_subtitles = 'big_buck_bunny.eng.srt'

    # We call all the methods
    mb_and_mv(input=cut)
    BBB_container(input=video)
    broadcasting(input=container)
    add_subtitles(input=video, subtitles=bbb_subtitles)


# We call the class ffmpeg()
ffmpeg()
