from yta_core.classes.segment_json import SegmentJson
from yta_core.enums.field import SegmentBuildingField
from yta_core.enums.type import SegmentType
from yta_core.edition_manual import EditionManual
from yta_core.enums.string_duration import EnhancementStringDuration
from yta_core.enums.mode import EnhancementMode
from yta_core.settings import Settings
from yta_core.builder import get_builder_class
from yta_core.database import database_handler
from yta_core.shortcodes.parser import shortcode_parser
from yta_core.audio.transcription import AudioTranscription
from yta_core.configuration import Configuration
from yta_core.configuration.condition.optional import DoShouldBuildNarration
from yta_audio_narration.narrator import MicrosoftVoiceNarrator
from yta_audio_silences import AudioSilence
from yta_audio_transcription import DefaultTimestampedAudioTranscriptor
from yta_temp import Temp
from yta_validation.parameter import ParameterValidator
from yta_file.handler import FileHandler
from yta_file.filename.handler import FilenameHandler
from yta_general_utils.logger import print_completed, print_in_progress
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from bson.objectid import ObjectId
from typing import Union


class Segment:
    """
    A segment within a Project that is able to build
    itself according to its configuration and values.
    """

    project_id: ObjectId
    """
    The project this segment belongs to.
    """
    index: int
    """
    The index of the segment, which identifies its
    order within the project.
    """
    status: str
    """
    The current status of the segment.
    """
    data: SegmentJson
    """
    The data that the segment has.
    """
    transcription: Union[AudioTranscription, None]
    """
    The audio voice narration transcription.
    """
    audio_filename: str
    """
    The filename of the audio file.
    """
    video_filename: str
    """
    The filename of the video file.
    """
    full_filename: str
    """
    The filename of the full file that includes
    audio and video.
    """

    @property
    def duration(
        self
    ) -> float:
        """
        The duration of the clip, that is read from
        the 'data' dict.
        """
        return self.data.duration
    
    @duration.setter
    def duration(
        self,
        value: float
    ) -> None:
        """
        Set the 'duration' property, that is located
        in the 'data' dict.
        """
        self.data.duration = value

    @property
    def voice_narration(
        self
    ) -> Union[dict, None]:
        """
        Get the dict that contains the information
        about the voice narration.
        """
        return self.data.voice_narration
    
    @property
    def voice_narration_filename_processed(
        self
    ) -> Union[str, None]:
        """
        Get the 'filename_processed' field from the
        voice narration.
        """
        if self.voice_narration is None:
            return None
        
        return self.voice_narration['filename_processed']
    
    @voice_narration_filename_processed.setter
    def voice_narration_filename_processed(
        self,
        value
    ):
        if self.voice_narration is None:
            raise Exception('Oops, something went when trying to set the voice narration...')
        
        self.data.voice_narration['filename_processed'] = value
    
    @property
    def has_voice_narration(
        self
    ) -> bool:
        """
        Check if the segment has a valid voice narration
        file that can be used for the building process,
        which means having the 'filename_processed'
        """
        return self.voice_narration_filename_processed

    @property
    def music(
        self
    ) -> Union[dict, None]:
        """
        Get the dict that contains the information
        about the music.
        """
        return self.data.music
    
    @property
    def music_filename_processed(
        self
    ) -> Union[str, None]:
        """
        Get the 'filename_processed' field from the
        voice narration.
        """
        if self.music is None:
            return None
        
        return self.music['filename_processed']

    @music_filename_processed.setter
    def music_filename_processed(
        self,
        value
    ):
        if self.music is None:
            raise Exception('Oops, something went wrong when trying to set the music...')
        
        self.data.voice_narration['filename_processed'] = value

    @property
    def has_music(
        self
    ) -> bool:
        """
        Check if the segment has a valid music file
        that can be used for the building process,
        which means having the 'filename_processed'
        """
        return self.music_filename_processed

    @property
    def has_audio_filename(
        self
    ) -> bool:
        """
        Check if the segment has an 'audio_filename' set.
        """
        return self.audio_filename is not None

    @property
    def audio_clip(
        self
    ) -> Union[AudioFileClip, None]:
        """
        The audio clip, from the audio filename if
        existing.
        """
        return self._audio_clip
        return (
            AudioFileClip(self.audio_filename)
            if self.has_audio_filename else
            None
        )
    
    @audio_clip.setter
    def audio_clip(
        self,
        value
    ) -> None:
        # TODO: Improve this
        self._audio_clip = value

    @property
    def has_audio_clip(
        self
    ) -> bool:
        """
        Check if the segment has an audio clip or not.
        """
        return self.audio_clip is not None
    
    @property
    def has_video_filename(
        self
    ) -> bool:
        """
        Check if the segment has a 'video_filename' set.
        """
        return self.video_filename is not None

    @property
    def video_clip(
        self
    ) -> Union[VideoFileClip, None]:
        """
        The video clip, from the video filename if
        existing.
        """
        return self._video_clip
        return (
            VideoFileClip(self.video_filename)
            if self.has_video_filename else
            None
        )

    @video_clip.setter
    def video_clip(
        self,
        value
    ) -> None:
        # TODO: Improve this
        self._video_clip = value
    
    @property
    def has_video_clip(
        self
    ) -> bool:
        """
        Check if the segment has a video clip or not.
        """
        return self.video_clip is not None
    
    @property
    def has_full_filename(
        self
    ) -> bool:
        """
        Check if the segment has a 'full_filename' set.
        """
        return self.full_filename is not None

    @property
    def full_clip(
        self
    ) -> Union[VideoFileClip, None]:
        """
        The full clip, including video and audio, from
        the full filename if existing.
        """
        return self._full_clip
        return (
            VideoFileClip(self.full_filename)
            if self.has_full_filename else
            None
        )
    
    @full_clip.setter
    def full_clip(
        self,
        value
    ) -> None:
        # TODO: Improve this
        self._full_clip = value
    
    @property
    def has_full_clip(
        self
    ) -> bool:
        """
        Check if the segment has a full clip or not.
        """
        return self.full_clip is not None

    @property
    def has_transcription(
        self
    ) -> bool:
        """
        Check if the segment has a transcription or not.
        """
        return self.transcription is not None

    @property
    def enhancements(
        self
    ) -> list['Enhancement']:
        """
        Get the enhancements as a list of Enhancement
        """
        # Import here due to cyclic import issue
        from yta_core.classes.enhancement import Enhancement

        if not hasattr(self, '_enhancements'):
            self._enhancements = [
                Enhancement(
                    self.project_id,
                    self.index,
                    self,
                    index + 100,
                    enhancement.as_dict
                ) for index, enhancement in enumerate(self.data.enhancements)
            ]

        return self._enhancements

    def __init__(
        self,
        project_id: ObjectId,
        index: int,
        data: dict
    ):
        ParameterValidator.validate_mandatory_instance_of('project_id', project_id, ObjectId)
        ParameterValidator.validate_mandatory_int('index', index)

        self.project_id = project_id
        self.index = index
        self.status = data.get(SegmentBuildingField.STATUS.value, None)

        self.data = SegmentJson()

        # TODO: What about 'status' that is both in 'data'
        # and as a specific attribute (?)
        for key in data:
            setattr(self.data, key, data[key])

        # TODO: Use 'set_audio_filename' (...) here (?)
        self.transcription = data.get(SegmentBuildingField.TRANSCRIPTION.value, None)
        self.audio_filename = data.get(SegmentBuildingField.AUDIO_FILENAME.value, None)
        self.audio_clip = (
            AudioFileClip(self.audio_filename)
            if self.audio_filename is not None else
            None
        )
        self.video_filename = data.get(SegmentBuildingField.VIDEO_FILENAME.value, None)
        self.video_clip = (
            VideoFileClip(self.video_filename)
            if self.video_filename is not None else
            None
        )
        self.full_filename = data.get(SegmentBuildingField.FULL_FILENAME.value, None)
        self.full_clip = (
            VideoFileClip(self.full_filename)
            if self.full_filename is not None else
            None
        )

    def build(
        self
    ):
        configuration = Configuration.get_configuration_by_type(self.data.type)

        if DoShouldBuildNarration.is_satisfied(configuration, self.data.as_dict):
            # 1. Step: Create voice narration
            if not self.has_audio_filename:
                self._create_voice_narration()

            # Force duration according to the audio
            #self.duration = self.audio_clip.duration
            # TODO: I'm doing this later, is it necessary
            # here? I think not (?)

            # 2. Step: Create transcription
            if not self.has_transcription:
                # TODO: Create transcription
                self._create_transcription()

            # 3. Step: Extract user shortcodes
            # TODO: Handle this (maybe status (?))
            self._extract_user_shortcodes()

            # 4. Step: Apply edition manual shortcodes
            self._apply_edition_manual()

        # TODO: What about duration here that is not set (?)
        # TODO: Should we '.set_duration' here to persist it (?)
        self.duration = (
            self.audio_clip.duration
            if self.has_audio_clip else
            self.duration
        )

        # 5. Step: Create visual (video) content
        if not self.has_video_filename:
            print_in_progress('Building base content step 4')
            self._build_video_content()
            print_completed('Base content built in step 4')

        # This would be the real duration that could be not the
        # one in the database as this is in real time and it is
        # not updated in the database
        self.duration = self.video_clip.duration

        # 6. Step: Compound video and audio (if necessary)
        if self.audio_clip:
            # If we have another audio clip we should want to put
            # them togeter, not to replace it
            audio = self.audio_clip
            if self.video_clip.audio:
                # We have another audio, we need to put them together
                # TODO: What about both audio lenghts? Are always
                # the same (?)
                audio = CompositeAudioClip([
                    self.video_clip.audio,
                    audio
                ])
                
            # TODO: Should we replace self.audio_clip (?)
            self.video_clip = self.video_clip.with_audio(audio)
        elif not self.video_clip.audio:
            # Premade and other type of video_clip can have audio
            # by themselves, but another type of videos cannot, so
            # we need to put silence audio to have an audio track
            # or we will have issues when concatenating with ffmpeg
            # in those clips without audio
            self.video_clip = self.video_clip.with_audio(
                AudioSilence.create(self.video_clip.duration)
            )

        # 7. Step: Update enhancements duration
        # TODO: By now I'm omitting this part
        self._update_enhancements_duration()
        # 8. Step: Build and apply enhancements
        # TODO: By now I'm omitting this part
        #self.build_step_6_build_and_apply_enhancements()

        # 9. Step: Build the final video
        self.full_clip = self.video_clip
        filename = self._create_segment_file('definitivo.mp4')
        self.full_clip.write_videofile(filename)
        self._set_full_filename(filename)

        self._set_as_finished()
        print_completed('Build completed')

    def _set_audio_filename(
        self,
        audio_filename: Union[str, None]
    ):
        """
        Set the 'audio_filename' parameter and update
        it in the database.
        """
        ParameterValidator.validate_string('audio_filename', audio_filename, do_accept_empty = False)

        self.audio_filename = audio_filename
        self.audio_clip = AudioFileClip(self.audio_filename)

        if audio_filename is not None:
            database_handler.update_project_segment_field(
                self.project_id,
                self.index,
                SegmentBuildingField.AUDIO_FILENAME.value,
                self.audio_filename
            )

    def _set_video_filename(
        self,
        video_filename: Union[str, None]
    ):
        """
        Set the 'video_filename' parameter and update
        it in the database.
        """
        ParameterValidator.validate_string('video_filename', video_filename, do_accept_empty = False)

        self.video_filename = video_filename
        self.video_clip = VideoFileClip(self.video_filename)

        if video_filename is not None:
            database_handler.update_project_segment_field(
                self.project_id,
                self.index,
                SegmentBuildingField.VIDEO_FILENAME.value,
                self.video_filename
            )

    def _set_full_filename(
        self,
        full_filename: Union[str, None]
    ):
        """
        Set the 'video_filename' parameter and update
        it in the database.
        """
        ParameterValidator.validate_string('full_filename', full_filename, do_accept_empty = False)

        self.full_filename = full_filename
        self.full_clip = VideoFileClip(self.full_filename)

        if full_filename is not None:
            database_handler.update_project_segment_field(
                self.project_id,
                self.index,
                SegmentBuildingField.FULL_FILENAME.value,
                self.full_filename
            )

    def _set_transcription(
        self,
        transcription: AudioTranscription
    ):
        """
        Set the transcription in the instance and also in
        the database.
        """
        ParameterValidator.validate_instance_of('transcription', transcription, 'AudioTranscription')

        # We have AudioTranscription from 'yta_audio', but
        # we want the one from 'yta_core'
        transcription = AudioTranscription(transcription.words)

        self.transcription = transcription

        if transcription is not None:
            database_handler.update_project_segment_field(
                self.project_id,
                self.index,
                SegmentBuildingField.TRANSCRIPTION.value,
                # TODO: Turn AudioTranscription (raw) into his wrapper
                self.transcription.for_mongo
            )

    def _set_shortcodes(
        self,
        shortcodes
    ):
        #  TODO: What type are these ones (?)
        self.shortcodes = shortcodes

        if shortcodes is not None:
            database_handler.update_project_segment_field(
                self.project_id,
                self.index,
                SegmentBuildingField.SHORTCODES.value,
                self.shortcodes
            )

    def _set_as_finished(
        self
    ):
        """
        Set the segment as finished (building has been
        completed).
        """
        database_handler.set_project_segment_as_finished(
            self.project_id,
            self.index
        )

    def _create_segment_file(
        self,
        filename: str
    ):
        """
        Create a filename within the definitive segments
        folder to keep the generated file locally and
        recover it later if something goes wrong.

        The definitive filename will be built using the 
        provided 'filename' and adding some more
        information in the name like the current segment
        index.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        return f'{Settings.DEFAULT_SEGMENT_PARTS_FOLDER}/segment_{self.index}_{Temp.get_filename(filename)}'
    
    def _create_voice_narration(
        self
    ):
        """
        Create the voice narration (if needed) by using
        AI, or copies the original voice narration to
        the definitive filename.
        """
        if self.has_voice_narration:
            # There is an audio file with the narration
            segment_part_filename = self._create_segment_file(f'narration.{FilenameHandler.get_extension(self.voice_narration_filename_processed)}')
            FileHandler.copy_file(self.voice_narration_filename_processed, segment_part_filename)
            print_completed('Original voice narration file copied to segment parts folder')
            self.voice_narration_filename_processed = segment_part_filename
            self._set_audio_filename(segment_part_filename)
        else:
            # The voice narration must be created
            segment_part_filename = self._create_segment_file('narration.wav')
            # TODO: Voice parameter need to change

            # TODO: Use the params in 'self.voice_narration' to build it
            def generate_voice_narration():
                engine = {
                    'microsoft': MicrosoftVoiceNarrator
                }[self.voice_narration['engine']]

                return engine.narrate(
                    text = self.voice_narration['text'],
                    name = self.voice_narration['narrator_name'],
                    emotion = self.voice_narration['emotion'],
                    speed = self.voice_narration['speed'],
                    pitch = self.voice_narration['pitch'],
                    language = self.voice_narration['language'],
                    output_filename = segment_part_filename
                )
            
            # TODO: I think we need to mix it with the music
            self._set_audio_filename(
                generate_voice_narration()
            )

            # self._set_audio_filename(
            #     MicrosoftVoiceNarrator.narrate(
            #         # TODO: How to get this field properly (?)
            #         self.data.text_to_narrate_sanitized_without_shortcodes,
            #         output_filename = segment_part_filename
            #     )
            # )
            print_completed('Voice narration created successfully')
        # TODO: Maybe we should do the '_set_audio_filename'
        # out of the if statement

    def _create_transcription(
        self
    ):
        """
        Create the transcription of the audio narration.

        Creates the transcription of the generated audio narration
        that would be stored in 'self.audio_filename'.
        
        This method returns a words array containing, for each word,
        a 'text', 'start' and 'end' field to be able to use the 
        transcription timestamps.
        """
        self._set_transcription(
            DefaultTimestampedAudioTranscriptor.transcribe(
                self.audio_filename,
                initial_prompt = self.data.text_to_narrate_sanitized_without_shortcodes
            )
        )

    def _extract_user_shortcodes(
        self
    ):
        shortcode_parser.parse(self.data.text_to_narrate)
        #self.shortcodes = shortcode_parser.shortcodes

        self._set_shortcodes(shortcode_parser.shortcodes)

        # TODO: Turn shortcodes into enhancements
        # TODO: I'm doing nothing with these enhancements
        # TODO: Maybe store in database (?)
        # TODO: Maybe I should manage this as 'user-enhancements'
        # enhancements = [
        #     shortcode.to_enhancement_element(self.transcription)
        #     for shortcode in self.shortcodes
        # ]

    def _apply_edition_manual(
        self
    ):
        # Import here due to cyclic import issue
        from yta_core.classes.enhancement import Enhancement

        # TODO: I need to dynamically get the edition manual from somewhere
        # By now I'm forcing it
        test_edition_manual = 'C:/Users/dania/Desktop/PROYECTOS/youtube-autonomous/youtube_autonomous/segments/enhancement/edition_manual/example.json'
        edition_manual = EditionManual.init_from_file(test_edition_manual)
        dict_enhancements_found = edition_manual.apply(self.transcription)
        print(dict_enhancements_found)
        # Turn dict enhancements found into Enhancement objects
        for index, dict_enhancement_found in enumerate(dict_enhancements_found):
            # TODO: What do we do with 'index' here (?)
            index = 100 + index
            self.enhancements.append(Enhancement(self.project_id, self.index, self, index, dict_enhancement_found))
        # TODO: Some enhancements could be incompatible due to collisions
        # or things like that

        # TODO: What about this enhancements (?)

    def _build_video_content(
        self
    ):
        builder = get_builder_class(SegmentType.to_enum(self.data.type))()
        # TODO: Is the 'data' enough (?)
        video_clip = builder.build_from_segment(self.data.as_dict)
        filename = self._create_segment_file('video.mp4')
        video_clip.write_videofile(filename)
        self._set_video_filename(filename)

    def _update_enhancements_duration(
        self
    ):
        # for index, enhancement in enumerate(self.data.enhancements):
        #     if PythonValidator.is_dict(enhancement):
        #         self.enhancements[index] = Enhancement(self.project_id, self.index, self, index + 100, enhancement)
        # # TODO: Convert dict enhancements to enhancement objects

        # 5. Update enhancements duration according to base video
        # TODO: What if 'start' is after the end of the base video (?)
        for index, enhancement in enumerate(self.enhancements):
            # With this condition we avoid the None enhancements that are 
            # generated due to the gap between the start indexes and the
            # ones we generate with +100 because of edition manual
            if enhancement is None:
                continue

            if enhancement.duration == EnhancementStringDuration.SEGMENT_DURATION.name:
                enhancement.duration = self.video_clip.duration

            if enhancement.start >= self.video_clip.duration:
                raise Exception('The enhancement start moment is after the video_clip.duration')
            
            end = enhancement.start + enhancement.duration
            if end > self.video_clip.duration:
                enhancement.duration = self.video_clip.duration - enhancement.start

            if enhancement.mode == EnhancementMode.INLINE.value:
                # If inline and start is after this moment, increase its
                # start as we are enlarging the video when applying this
                # inline enhancement
                for i in range(index + 1, len(self.enhancements)):
                    if self.enhancements[i] is None:
                        continue
                    
                    if self.enhancements[i].start >= enhancement.start:
                        self.enhancements[i].start += enhancement.duration
