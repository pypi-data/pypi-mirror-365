import json
import logging
import os
import time

from alibabacloud_ice20201109 import models as ice20201109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_ims_editing_mcp_server.tools.tool_registration import *
from alibabacloud_ims_editing_mcp_server.tools.param_type import *
from alibabacloud_ims_editing_mcp_server.client import ice_client, invoke_api
from Tea.exceptions import TeaException


@register_level_tools(basic_tool, trial_tool, tool_info={
    'tags': {'提交阶段', '提交任务', '普通剪辑'}
})
def submit_media_producing_job(
        timeline: Annotated[dict, Field(description="剪辑时间线，需要注意是一个标准的JSON格式")],
        output_media_config: Annotated[OutputMediaConfig, Field(description="输出配置")]) -> str:
    """
        <tags>'提交阶段','提交任务','普通剪辑'</tags>
        <useCases>
            <useCase>只拼接视频, 剪辑合成视频，并输出到指定的oss地址，返回剪辑jobId</useCase>
            <useCase>根据输入的时间线, 剪辑合成视频，并输出到指定的oss地址，返回剪辑jobId</useCase>
        </useCases>
        <subscriptionLevel>Basic</subscriptionLevel>
       如果客户没有传入OutputBucket 或 OutputFileName，需要和客户明确输出文件信息。
        Args:
            timeline (dict): 剪辑时间线，需要注意是一个标准的JSON格式！！！主要包含以下字段：
              VideoTracks: 视频轨道
                VideoTrackClips: 视频轨素材片段列表。
                  MediaId:媒资ID
                  In: 素材片段的起始时间点，单位为秒，取值范围为[0, 视频时长)，其中起始时间点必须小于终止时间点。
                  Out: 素材片段的终止时间点，单位为秒，取值范围为(起始时间点, 视频时长]，其中起始时间点必须小于终止时间点。
                ...

            output_media_config (dict): 输出配置
                OutputBucket: 输出的OSS bucket名称，示例 test-bucket
                OutputFileName: 输出的OSS文件名，包含文件后缀，示例 test.mp4
                Width: 输出宽度，非必填
                Height: 输出宽度，非必填


            Timeline Examples:
          1. 视频多段截取合成示例（本示例演示如何截取一个视频里时域在 5-15 秒、25-35 秒、50-60 秒的内容，并重新合成一个视频。）请求参数如下:
          {
            "VideoTracks": [{
               "VideoTrackClips": [
                {
                   "MediaId": "test_media_id_1",
                   "In": 5,
                   "Out": 15
                },
                {
                   "MediaId": "test_media_id_1",
                   "In": 25,
                   "Out": 35
                },
                {
                   "MediaId": "test_media_id_1",
                   "In": 50,
                   "Out": 60
                }]
            }]
          }
        """
    region = os.getenv('ALIBABA_CLOUD_REGION')
    output_media_config = output_media_config.model_dump()
    output_bucket = output_media_config["OutputBucket"]
    output_name = output_media_config["OutputFileName"]
    width = None
    height = None
    if "Width" in output_media_config:
        width = output_media_config["Width"]
    if "Height" in output_media_config:
        height = output_media_config["Height"]

    job_output_config_str = json.dumps(
        {"MediaURL": f"http://{output_bucket}.oss-{region}.aliyuncs.com/{output_name}", "Width": width,
         "Height": height}).encode("utf-8")
    timeline_str = json.dumps(timeline).encode('utf-8')

    logging.info(f'submit_media_producing_job, timeline: {timeline_str}, output_media_config: {job_output_config_str}')

    submit_media_producing_job_request = ice20201109_models.SubmitMediaProducingJobRequest(
        timeline=timeline_str,
        output_media_config=job_output_config_str
    )
    runtime = util_models.RuntimeOptions()
    try:
        resp = ice_client.submit_media_producing_job_with_options(submit_media_producing_job_request, runtime)
        jobId = resp.body.job_id
        logging.info(jobId)
        return jobId
    except Exception as error:
        logging.exception(error)
        return str(error)


@register_level_tools(basic_tool, trial_tool, tool_info={
    'tags': {'提交阶段', '查询任务', '普通剪辑'}
})
def get_media_producing_job(jobId: Annotated[str, Field(description="剪辑任务ID")]) -> str:
    """
    <tags>'提交阶段','查询任务','普通剪辑'</tags>
    <subscriptionLevel>Basic</subscriptionLevel>
    <toolDescription>查询单个剪辑任务的状态，并返回任务结果。</toolDescription>
    <return>任务失败会返回错误信息，如果还在处理，会返回"The job is processing"，如果任务成功，则会返回任务的详细信息，包含成片的url、时间线、时长等信息</return>
    """
    get_media_producing_job_request = ice20201109_models.GetMediaProducingJobRequest(
        job_id=jobId
    )
    get_media_producing_job_response = ice_client.get_media_producing_job(get_media_producing_job_request)

    logging.info(get_media_producing_job_response.body)
    if get_media_producing_job_response.body.media_producing_job.status == "Success" or get_media_producing_job_response.body.media_producing_job.status == "Finished" or get_media_producing_job_response.body.media_producing_job.status == "S3UploadSuccess":
        return str(get_media_producing_job_response.body.media_producing_job)
    elif get_media_producing_job_response.body.media_producing_job.status == "Failed" or get_media_producing_job_response.body.media_producing_job.status == "S3UploadFailed":
        return "the job failed because of " + get_media_producing_job_response.body.media_producing_job.message
    else:
        return "the job is processing"


@register_level_tools(basic_tool, trial_tool, tool_info={
    'tags': {'提交阶段', '提交任务', '批量成片', '脚本化'}
})
def submit_batch_editing_script_job(
        media_group_array: Annotated[list, Field(description="素材分组列表")],
        output_config: Annotated[dict, Field(description="输出配置，包含输出成片的个数、输出地址、输出时长、输出宽高、是否仅生成预览不合成等配置")],
        speech_text_array: Annotated[Optional[list], Field(description="全局口播文案列表，每条口播对应一个完整成片")] = None,
        input_config: Annotated[Optional[dict], Field(description="除素材和口播文案外，其他的输入配置，包含标题、贴纸、背景音乐、背景图等，都非必填，如果没有明确需求，不需要填写")] = None,
        editing_config: Annotated[Optional[dict], Field(description="剪辑配置，包含标题样式配置、口播配置、混剪处理配置等，无特殊要求可以不填")] = None,
        user_data: Annotated[Optional[dict], Field(description="用户业务配置、回调配置")] = None):
    """
    <tags>'提交阶段','提交任务','批量成片','脚本化'</tags>
    <subscriptionLevel>Basic</subscriptionLevel>
    <toolDescription>该工具主要用于提交批量成片脚本化任务。脚本化成片是通过结构化的“剪辑脚本”来驱动批量视频生成的一种高级剪辑模式，其核心是 分组控制 + 精确编排。分组控制：可将素材划分为多个逻辑分组（如“开场”、“产品展示”、“用户评价”等），每个分组可独立配置素材、文案、时长、音量等参数，成片按分组顺序拼接，结构清晰可控；精确控制素材来源：每个镜头使用的素材严格限定在指定分组内，不会从其他组或全局池中随机选取，适合需要“指定画面配指定文案”的强结构化需求。脚本化成片任务多用于营销混剪，支持一次输出多个成片。此任务有两种模式，全局口播模式和分组口播模式。</toolDescription>
    <useCases>
        <useCase>全局口播模式下，一条口播对应一个完整成片，多个分组的素材按分组顺序前后拼接，直到与口播文案的时长相当，全局的口播文案配置在speech_text_array中；当给一批素材，和好几段完整的口播，进行批量混剪，则应该使用全局口播模式。</useCase>
        <useCase>分组口播模式下，是每个分组的素材对应当前分组中的口播，多段口播和素材前后拼接，形成完整的口播文案和视频内容，分组口播文案配置在素材分组里media_group_array.SpeechTextArray. 如果客户的需求是给好几个分组的素材，其中每个分组各自对应一些口播文案，则应该使用分组口播模式。</useCase>
    </useCases>

    Args:
        media_group_array: 素材分组列表，每个素材分组Media_Group包含以下字段
            GroupName (string): 分组名，此字段如果客户未提供，自动按照Group1、Group2 ... 依序赋值。分组名不允许重复，不超过50个字符。
            MediaArray (list[object]): 素材列表，支持媒资ID或者媒资URL，支持配置多段入出点。示例：[{"Media": "mediaId11"}, {"Media": "https://test-bucket.oss-cn-shanghai.aliyuncs.com/test1.mp4", "TimeRangeList": [{"In": 0, "Out": 3}, {"In": 5, "Out": 10}]}]
                Media: 支持媒资ID或者媒资URL。这个字段需要客户明确提供，如果客户未说明，需要提示客户输入。示例："mediaId11"，或 "https://test-bucket.oss-cn-shanghai.aliyuncs.com/test1.mp4".
                TimeRangeList (list[object]): 素材入出点列表，如果客户未明确说明，不需要配置。如果配置后，成片仅会选取入出点范围内的片段合成。
                    In (float): 素材片段的起始时间点，单位为秒.
                    Out (float): 素材片段的终止时间点，单位为秒.
            SpeechTextArray (list[string]): 当前分组内的口播文案列表，每次合成随机选一个，最多50个，每条口播文案最长1000个字符。非必填字段，如果客户输入里不需要分组文案时，不需要填写。
            Duration (float): 当前分组对应的时长，单位秒。仅限SpeechTextArray为空时填写。非必填字段。
            Volume (float): 当前分组内视频的音量，取值范围[0, 10.0]。0为静音，1为原始音量。非必填字段。
        speech_text_array: 全局口播文案列表，每条口播对应一个完整成片。每次合成随机选一个，最多50个，每条口播文案最长1000个字符。非必填字段，如果客户输入里不需要口播文案时，不需要填写。这个字段和media_group_array里的SpeechTextArray互斥，最多只能填写一处。
        input_config: 除素材和口播文案外，其他的输入配置，包含标题、贴纸、背景音乐、背景图等，都非必填，如果没有明确需求，不需要填写。
            TitleArray (list[string]): 标题列表，每次合成随机选一个，标题在整个成片中都会出现。
            StickerArray (list[object]): 贴纸列表，每次合成随机选一个，贴纸在整个成片中都会出现。每个贴纸素材Sticker包含以下参数。
                MediaId (string): 贴纸素材媒资ID。MediaId 和 MediaURL二选一必填，只需要填一个
                MediaURL (string): 贴纸素材OSS URL。MediaId 和MediaURL二选一必填，只需要填一个
                X (float): 贴纸左上角距离输出视频左上角的横向距离，取值为0 ~ 0.9999时，表示相对输出视频宽的占比。取值为>=2的整数时，表示绝对像素。
                Y (float): 贴纸左上角距离输出视频左上角的纵向距离，取值为0 ~ 0.9999时，表示相对输出视频高的占比。取值为>=2的整数时，表示绝对像素。
                Width (int): 表示贴纸在输出视频中的宽度。当取值为[0～0.9999]时，表示相对输出视频宽的占比。当取值为>=2的整数时，表示绝对像素。
                Height (int): 表示贴纸在输出视频中的高度。当取值为[0～0.9999]时，表示相对输出视频宽的占比。当取值为>=2的整数时，表示绝对像素。
                DyncFrames (int): 动图的帧数，取值范围[0,100]，一般为25。仅当贴纸是动图gif时需要填写。
                Opacity (float): 透明度，取值范围[0,1]，0为全透明，1为全不透明，默认为1。
            BackgroundMusicArray (list[string]): 背景音乐数组，每次合成随机选一个。最多50个，支持媒资ID 或 OSS URL。
            BackgroundImageArray (list[string]): 背景图片数组，每次合成随机选择一个。最多50个，支持媒资ID 或 OSS URL。

        output_config: 输出配置，包含输出成片的个数、输出地址、输出时长、输出宽高、是否仅生成预览不合成等配置。其中 OutputBucket、OutputFileName、Width、Height 必填，如果没有客户未明确说明，需要提示用户输入。
            Count (int): 输出成片的数量，上限为100，默认值为1。
            OutputBucket (string): 输出成片的oss存储bucket，示例：your-bucket
            OutputFileName (string): 输出成片的oss文件名，OutputFileName中必须包含{index}占位符，如果不包含{index}，需要提示客户加上。示例：test_dir/test_output_{index}.mp4。
            FixedDuration (float): 输出视频单片的固定时长，单位秒。如果设置了固定时长，视频时长将会对齐此参数。分组口播模式不支持设置该参数；全局口播模式下，在SpeechTextArray为空的情况下可支持设置此参数。
            Width (int): 输出视频宽度，单位：像素。示例：1920
            Height (int): 输出视频高度，单位：像素。示例: 1080

        editing_config (dict): 剪辑配置，包含标题样式配置、口播配置、混剪处理配置等，无特殊要求可以不填。
        user_data (dict): 用户业务配置、回调配置。示例：{"NotifyAddress":"https://xx.xx.xxx"}或{"NotifyAddress":"ice-callback-demo"}，NotifyAddress 支持配置http回调地址 或 mns消息队列名称

    Returns:
        job_id: 任务ID，可调用get_batch_editing_job查询任务信息

    入参示例：
    1、全局口播模式
    {
        "media_group_array": [{
                "GroupName": "Group1",
                "MediaArray": [{"Media": "mediaId1"}, {"Media": "mediaId2"}]
            },{
                "GroupName": "Group2",
                "MediaArray": [{"Media": "mediaId3"}, {"Media": "mediaId4"}]
            },{
                "GroupName": "Group3",
                "MediaArray": [{"Media": "mediaId5"}, {"Media": "mediaId6"}]
            }
        ],
        "SpeechTextArray": ["Hello world! Alice", "My name is Jack"],
        "output_config": {
            "OutputBucket": "your-bucket",
            "OutputFileName": "test_dir/test_output_{index}.mp4",
            "Width": 1920,
            "Height": 1080,
            "Count": 2
        }
    }
    最终生成两条视频，口播文案分别为"Hello world! Alice" 和 "My name is Jack".

    2、分组口播模式：
    {
        "media_group_array": [{
                "GroupName": "Group1",
                "MediaArray": [{"Media": "mediaId1"}, {"Media": "mediaId2","TimeRangeList": [{"In": 0, "Out": 3}, {"In": 5, "Out": 10}]}],
                "Duration": 3,
                "Volume": 1
            },{
                "GroupName": "Group2",
                "MediaArray": [{"Media": "mediaId3"}, {"Media": "mediaId4"}],
                "SpeechTextArray": ["Hello world!", "My name is "],
                "Volume": 1
            },{
                "GroupName": "Group3",
                "MediaArray": [{"Media": "mediaId5"}, {"Media": "mediaId6"}],
                "SpeechTextArray": ["Alice", "Jack"],
                "Volume": 1
            }
        ],
        "output_config": {
            "OutputBucket": "your-bucket",
            "OutputFileName": "test_dir/test_output_{index}.mp4",
            "Width": 1920,
            "Height": 1080,
            "Count": 2
        }
    }
    最终生成两个成片，两个成片的前3s没有口播文案，3s后的口播文案分别是 "Hello world! Alice" 和 "My name is Jack"，最终完整的文案为多个分组文案拼接的结果。

    """
    if input_config is None:
        input_config = {}

    if media_group_array is None:
        return "error: media_group_array is mandatory"

    media_meta_data_array = []

    for media_group in media_group_array:
        if "MediaArray" not in media_group:
            return "error: media_group_array.MediaArray is mandatory"
        if "GroupName" not in media_group:
            return "error: media_group_array.GroupName is mandatory"
        media_array = media_group["MediaArray"]
        media_pure_list = []
        for media in media_array:
            if "Media" not in media:
                return "error: media_group_array.MediaArray.Media is mandatory"
            media_pure_list.append(media["Media"])
            if "TimeRangeList" in media:
                time_range_list = []
                for time_range in media["TimeRangeList"]:
                    if "In" in time_range and "Out" in time_range:
                        time_range_list.append(time_range)
                media_meta_data = {
                    "Media": media["Media"],
                    "GroupName": media_group["GroupName"],
                    "TimeRangeList": time_range_list
                }
                media_meta_data_array.append(media_meta_data)
        media_group["MediaArray"] = media_pure_list

    if len(media_meta_data_array) > 0:
        if editing_config is None:
            editing_config = {}
        if "MediaConfig" not in editing_config:
            media_config = {}
            editing_config["MediaConfig"] = media_config

        editing_config["MediaConfig"]["MediaMetaDataArray"] = media_meta_data_array

    input_config["MediaGroupArray"] = media_group_array
    if speech_text_array:
        input_config["SpeechTextArray"] = speech_text_array

    if output_config is None:
        return "output_config is mandatory"

    if "OutputBucket" not in output_config:
        return "OutputBucket is mandatory"

    if "OutputFileName" not in output_config:
        return "OutputFileName is mandatory"

    if "{index}" not in output_config["OutputFileName"]:
        return "OutputFileName should contains {index}."

    output_bucket = output_config["OutputBucket"]
    output_name = output_config["OutputFileName"]
    region = os.getenv('ALIBABA_CLOUD_REGION')

    output_config["MediaURL"] = f"http://{output_bucket}.oss-{region}.aliyuncs.com/{output_name}"

    output_config.pop("OutputBucket", None)
    output_config.pop("OutputFileName", None)

    input_config_str = json.dumps(input_config, ensure_ascii=False)
    output_config_str = json.dumps(output_config, ensure_ascii=False)

    editing_config_str = None
    user_data_str = None

    if editing_config:
        editing_config_str = json.dumps(editing_config, ensure_ascii=False)
    if user_data:
        user_data_str = json.dumps(user_data, ensure_ascii=False)

    return submit_batch_media_producing_job(input_config_str, output_config_str, editing_config_str, user_data_str)


@register_level_tools(standard_tool, trial_tool, tool_info={
    'tags': {'提交阶段', '提交任务', '批量成片', '图文匹配'}
})
def submit_batch_editing_general_match_job(media_array: Annotated[list,Field(description="素材列表，支持媒资ID或者媒资URL，支持配置多段入出点")],
                                           speech_text_array: Annotated[list,Field(description="口播列表，每一条口播对应一个完整成片，如果希望最终的成片是由多段小的口播文案拼接而成，需要将多段小的口播文案拼接在一起，中间用逗号分割，拼成一条长的口播文案再传入")],
                                           output_config: Annotated[dict,Field(description="输出配置，包含输出成片的个数、输出地址、输出时长、输出宽高、是否仅生成预览不合成等配置")],
                                           input_config: Annotated[Optional[dict],Field(description="除素材和口播文案外，其他的输入配置，包含标题、贴纸、背景音乐、背景图等，都非必填，如果没有明确需求，不需要填写")] = None,
                                           editing_config: Annotated[Optional[dict],Field(description="剪辑配置，包含标题样式配置、口播配置、混剪处理配置等，无特殊要求可以不填")] = None,
                                           user_data: Annotated[Optional[dict],Field(description="用户业务配置、回调配置")] = None) -> str:
    """
    <tags>'提交阶段','提交任务','批量成片','图文匹配'</tags>
    <subscriptionLevel>Standard</subscriptionLevel>
    <toolDescription>该工具主要用于提交图文匹配批量成片，会自动针对文案匹配最合适的素材进行匹配成片，多用于文案需要和画面对应的剪辑场景。支持一次输出一个或多个成片。</toolDescription>
    Args:
        media_array (list[object]): 素材列表，支持媒资ID或者媒资URL，支持配置多段入出点。示例：[{"Media": "mediaId11"}, {"Media": "https://test-bucket.oss-cn-shanghai.aliyuncs.com/test1.mp4", "TimeRangeList": [{"In": 0, "Out": 3}, {"In": 5, "Out": 10}]}]
                Media: 支持媒资ID或者媒资URL。这个字段需要客户明确提供，如果客户未说明，需要提示客户输入。示例："mediaId11"，或 "https://test-bucket.oss-cn-shanghai.aliyuncs.com/test1.mp4".
                TimeRangeList (list[object]): 素材入出点列表，如果客户未明确说明，不需要配置。如果配置后，成片仅会选取入出点范围内的片段合成。
                    In (float): 素材片段的起始时间点，单位为秒.
                    Out (float): 素材片段的终止时间点，单位为秒.
        speech_text_array (list[string]): 口播列表，每一条口播对应一个完整成片，如果希望最终的成片是由多段小的口播文案拼接而成，需要将多段小的口播文案拼接在一起，中间用逗号分割，拼成一条长的口播文案再传入。
        input_config: 除素材和口播文案外，其他的输入配置，包含标题、贴纸、背景音乐、背景图等，都非必填，如果没有明确需求，不需要填写。
            TitleArray (list[string]): 标题列表，每次合成随机选一个，标题在整个成片中都会出现。
            StickerArray (list[object]): 贴纸列表，每次合成随机选一个，贴纸在整个成片中都会出现。每个贴纸素材Sticker包含以下参数。
                MediaId (string): 贴纸素材媒资ID。MediaId 和 MediaURL二选一必填，只需要填一个
                MediaURL (string): 贴纸素材OSS URL。MediaId 和MediaURL二选一必填，只需要填一个
                X (float): 贴纸左上角距离输出视频左上角的横向距离，取值为0 ~ 0.9999时，表示相对输出视频宽的占比。取值为>=2的整数时，表示绝对像素。
                Y (float): 贴纸左上角距离输出视频左上角的纵向距离，取值为0 ~ 0.9999时，表示相对输出视频高的占比。取值为>=2的整数时，表示绝对像素。
                Width (int): 表示贴纸在输出视频中的宽度。当取值为[0～0.9999]时，表示相对输出视频宽的占比。当取值为>=2的整数时，表示绝对像素。
                Height (int): 表示贴纸在输出视频中的高度。当取值为[0～0.9999]时，表示相对输出视频宽的占比。当取值为>=2的整数时，表示绝对像素。
                DyncFrames (int): 动图的帧数，取值范围[0,100]，一般为25。仅当贴纸是动图gif时需要填写。
                Opacity (float): 透明度，取值范围[0,1]，0为全透明，1为全不透明，默认为1。
            BackgroundMusicArray (list(string)): 背景音乐数组，每次合成随机选一个。最多50个，支持媒资ID 或 OSS URL。
            BackgroundImageArray (list[string]): 背景图片数组，每次合成随机选择一个。最多50个，支持媒资ID 或 OSS URL。
        output_config: 输出配置，包含输出成片的个数、输出地址、输出时长、输出宽高、是否仅生成预览不合成等配置。其中 OutputBucket、OutputFileName、Width、Height 必填，如果没有客户未明确说明，需要提示用户输入。
            Count (int): 输出成片的数量，上限为100，默认值为1。
            OutputBucket (string): 输出成片的oss存储bucket，示例：your-bucket。如果客户未明确说明，需要引导客户输入。
            OutputFileName (string): 输出成片的oss文件名，OutputFileName中必须包含{index}占位符，如果不包含{index}，需要提示客户加上。示例：test_dir/test_output_{index}.mp4。
            Width (int): 输出视频宽度，单位：像素。示例：1920
            Height (int): 输出视频高度，单位：像素。示例: 1080
        editing_config (dict): 剪辑配置，包含标题样式配置、口播配置、混剪处理配置等，无特殊要求可以不填。
        user_data (dict): 用户业务配置、回调配置。示例：{"NotifyAddress":"https://xx.xx.xxx"}或{"NotifyAddress":"ice-callback-demo"}，NotifyAddress 支持配置http回调地址 或 mns消息队列名称

    Returns:
        job_id: 任务ID，可调用get_batch_editing_job查询任务信息

    入参示例：
    {
        "media_array": [{"Media": "mediaId1"}, {"Media": "mediaId2","TimeRangeList": [{"In": 0, "Out": 3}, {"In": 5, "Out": 10}]}],
        "speech_text_array": ["Hello world! Alice", "My name is Jack"],
        "output_config": {
            "OutputBucket": "your-bucket",
            "OutputFileName": "test_dir/test_output_{index}.mp4",
            "Width": 1920,
            "Height": 1080,
            "Count": 2
        }
    }
    最终生成两条视频，口播文案分别为"Hello world! Alice" 和 "My name is Jack"，成片的画面会挑选和口播文案最匹配的片段，前后拼接成片。

    """
    if input_config is None:
        input_config = {}
    input_config["SceneInfo"] = {"Scene": "General"}
    input_config["SpeechTextArray"] = speech_text_array

    if media_array is None:
        return "error: media_array is mandatory"

    media_meta_data_array = []
    media_pure_list = []

    for media in media_array:
        if "Media" not in media:
            return "error: media_group_array.MediaArray.Media is mandatory"
        media_pure_list.append(media["Media"])
        if "TimeRangeList" in media:
            time_range_list = []
            for time_range in media["TimeRangeList"]:
                if "In" in time_range and "Out" in time_range:
                    time_range_list.append(time_range)
            media_meta_data = {
                "Media": media["Media"],
                "TimeRangeList": time_range_list
            }
            media_meta_data_array.append(media_meta_data)

    if len(media_meta_data_array) > 0:
        if editing_config is None:
            editing_config = {}
        if "MediaConfig" not in editing_config:
            media_config = {}
            editing_config["MediaConfig"] = media_config

        editing_config["MediaConfig"]["MediaMetaDataArray"] = media_meta_data_array

    input_config["MediaArray"] = media_pure_list

    if output_config is None:
        return "output_config is mandatory"

    if "OutputBucket" not in output_config:
        return "OutputBucket is mandatory"

    if "OutputFileName" not in output_config:
        return "OutputFileName is mandatory"

    if "{index}" not in output_config["OutputFileName"]:
        return "OutputFileName should contains {index}."

    output_bucket = output_config["OutputBucket"]
    output_name = output_config["OutputFileName"]
    region = os.getenv('ALIBABA_CLOUD_REGION')

    output_config["MediaURL"] = f"http://{output_bucket}.oss-{region}.aliyuncs.com/{output_name}"

    output_config.pop("OutputBucket", None)
    output_config.pop("OutputFileName", None)

    input_config_str = json.dumps(input_config, ensure_ascii=False)
    output_config_str = json.dumps(output_config, ensure_ascii=False)

    editing_config_str = None
    user_data_str = None

    if editing_config:
        editing_config_str = json.dumps(editing_config, ensure_ascii=False)
    if user_data:
        user_data_str = json.dumps(user_data, ensure_ascii=False)

    return submit_batch_media_producing_job(input_config_str, output_config_str, editing_config_str, user_data_str)


def submit_batch_media_producing_job(input_config: str, output_config: str, editing_config: str = None,
                                     user_data: str = None) -> str:
    submit_batch_media_producing_request = ice20201109_models.SubmitBatchMediaProducingJobRequest(
        input_config=input_config,
        output_config=output_config,
        editing_config=editing_config,
        user_data=user_data
    )
    runtime = util_models.RuntimeOptions()
    try:
        resp = ice_client.submit_batch_media_producing_job_with_options(submit_batch_media_producing_request, runtime)
        job_id = resp.body.job_id
        logging.info(job_id)
        return job_id
    except Exception as error:
        logging.exception(error)
        return str(error)


@register_level_tools(standard_tool, trial_tool, tool_info={
    'tags': {'提交阶段', '查询任务', '批量成片'}
})
def get_batch_editing_job(job_id: Annotated[str,Field(description="任务ID")]) -> str:
    """
    <tags>'提交阶段','查询任务','批量成片'</tags>
    <subscriptionLevel>Standard</subscriptionLevel>
    <toolDescription>该工具主要用于查询批量成片任务，并返回任务结果。一个批量成片任务包含做个子剪辑任务。</toolDescription>
    <return>如果任务失败，会返回报错信息，如果还在处理，会返回任务处理中，如果任务成功，则会返回主任务的信息，比如状态、任务配置，以及所有子任务的任务信息，包含状态、成片时长、成片URL等。</return>
    """
    get_batch_media_producing_job_request = ice20201109_models.GetBatchMediaProducingJobRequest(
        job_id=job_id
    )
    get_batch_media_producing_job_response = ice_client.get_batch_media_producing_job(
        get_batch_media_producing_job_request)
    logging.info(get_batch_media_producing_job_response.body)
    if get_batch_media_producing_job_response.body.editing_batch_job.status == "Finished":
        return json.dumps(get_batch_media_producing_job_response.body.to_map(), ensure_ascii=False)
    elif get_batch_media_producing_job_response.body.editing_batch_job.status == "Failed":
        reason = None
        if get_batch_media_producing_job_response.body.editing_batch_job.extend:
            extend_json = json.loads(get_batch_media_producing_job_response.body.editing_batch_job.extend)
            if "ErrorMessage" in extend_json:
                reason = extend_json["ErrorMessage"]
                return "the job failed with reason: " + reason
        return "the job failed"
    else:
        return "the job is processing"


@register_level_tools(basic_tool, trial_tool, tool_info={
    'tags': {'时间线处理阶段', '时间线操作'}
})
def generate_timeline(
        text: Annotated[str, Field(
            description="剪辑意图，最终想要生成什么样的视频，素材应该如何编排，是否需要应用转场特效等效果，是否需要文字转语音、语音识别文字等智能处理。")],
        material: Annotated[MaterialData, Field(description="素材信息，包含视频、音频、图片、字幕等素材信息。")],
        output_width: Annotated[int, Field(description="输出视频的宽，单位为像素。")],
        output_height: Annotated[int, Field(description="输出视频的高，单位为像素。")]) -> str:
    """
        <tags>'时间线处理阶段','时间线操作'</tags>
        <subscriptionLevel>Basic</subscriptionLevel>
        <toolDescription>该工具根据明确的剪辑意图，生成剪辑时间线。</toolDescription>

        Args:
            text (string): 剪辑意图，最终想要生成什么样的视频，素材应该如何编排，是否需要应用转场特效等效果，是否需要文字转语音、语音识别文字等智能处理。
            material (dict): 剪辑素材，包含以下字段。
                video_list (list): 视频素材列表。
                    {
                        MediaId (str): 媒资ID,与媒资URL选填一个
                        MediaURL (str): 媒资URL，与媒资ID选填一个
                        In (float): 媒资截取片段的入点
                        Out (float): 媒资截取片段的出点
                    }
                audio_list (list): 音频素材列表
                    {
                        MediaId (str): 媒资ID,与媒资URL选填一个
                        MediaURL (str): 媒资URL，与媒资ID选填一个
                        In (float): 媒资截取片段的入点
                        Out (float): 媒资截取片段的出点
                    }
                image_list (list): 图片素材列表
                    {
                        MediaId (str): 媒资ID,与媒资URL选填一个
                        MediaURL (str): 媒资URL，与媒资ID选填一个
                    }
                subtitle_list (list): 字幕素材列表
                    {
                        MediaId (str): 媒资ID,与媒资URL选填一个
                        MediaURL (str): 媒资URL，与媒资ID选填一个
                    }
            output_width (int): 输出视频的宽度
            output_height (int): 输出视频的高度
    """

    material = material.model_dump()

    video_list = material['video_list'] if 'video_list' in material else []
    audio_list = material['audio_list'] if 'audio_list' in material else []
    image_list = material['image_list'] if 'image_list' in material else []
    subtitle_list = material['subtitle_list'] if 'subtitle_list' in material else []

    input_config = {
        "video_list": video_list,
        "audio_list": audio_list,
        "image_list": image_list,
        "subtitle_list": subtitle_list
    }

    output_config = {
        "Width": output_width,
        "Height": output_height
    }

    payload = {
        "Prompt": text,
        "Mode": "Create",
        "InputConfig": json.dumps(input_config),
        "OutputConfig": json.dumps(output_config)
    }

    try:

        response = invoke_api('SubmitTimelineGenerateJob', payload)
        job_id = response['JobId']

        payload = {
            "JobId": job_id
        }

        while True:
            response = invoke_api('GetSmartHandleJob', payload)
            status = response['State']

            if status == 'Finished':
                return response['JobResult']['AiResult']
            elif status == 'Failed':
                return response['ErrorMessage'] if 'ErrorMessage' in response and response['ErrorMessage'] != '' else "Timeline Generate Failed"
            else:
                time.sleep(5)
    except TeaException as te:
        return te.data['Message']
    except Exception as e:
        print(e)
        return "Timeline Generate Failed, Exception Occurred"


@register_level_tools(basic_tool, trial_tool, tool_info={
    'tags': {'时间线处理阶段', '时间线操作'}
})
def modify_timeline(text: Annotated[str, Field(
    description="剪辑意图，最终想要生成什么样的视频，素材应该如何编排，是否需要应用转场特效等效果，是否需要文字转语音、语音识别文字等智能处理。")],
                    material: Annotated[
                        MaterialData, Field(description="素材信息，包含视频、音频、图片、字幕等素材信息。")],
                    timeline: Annotated[Dict, Field(description="需要被修改的时间线")],
                    output_width: Annotated[int, Field(description="输出视频的宽，单位为像素。")],
                    output_height: Annotated[int, Field(description="输出视频的高，单位为像素。")]) -> str:
    """
        <tags>'时间线处理阶段','时间线操作'</tags>
        <subscriptionLevel>Basic</subscriptionLevel>
        <toolDescription>根据输入的text来修改生成的时间线，只需传入修改相关的命令。素材列表只能传入新增的素材内容。</toolDescription>

       Args:
            text (string): 剪辑意图，最终想要生成什么样的视频，素材应该如何编排，是否需要应用转场特效等效果，是否需要文字转语音、语音识别文字等智能处理。
            material (dict): 新增的素材内容，包含以下字段。
                video_list (list): 视频素材列表。
                    {
                        MediaId (str): 媒资ID,与媒资URL选填一个
                        MediaURL (str): 媒资URL，与媒资ID选填一个
                        In (float): 媒资截取片段的入点
                        Out (float): 媒资截取片段的出点
                    }
                audio_list (list): 音频素材列表
                    {
                        MediaId (str): 媒资ID,与媒资URL选填一个
                        MediaURL (str): 媒资URL，与媒资ID选填一个
                        In (float): 媒资截取片段的入点
                        Out (float): 媒资截取片段的出点
                    }
                image_list (list): 图片素材列表
                    {
                        MediaId (str): 媒资ID,与媒资URL选填一个
                        MediaURL (str): 媒资URL，与媒资ID选填一个
                    }
                subtitle_list (list): 字幕素材列表
                    {
                        MediaId (str): 媒资ID,与媒资URL选填一个
                        MediaURL (str): 媒资URL，与媒资ID选填一个
                    }
            timeline (dict): 需要被修改的原始时间线
            output_width (int): 输出视频的宽度
            output_height (int): 输出视频的高度
    """

    material = material.model_dump()

    video_list = material['video_list'] if 'video_list' in material else []
    audio_list = material['audio_list'] if 'audio_list' in material else []
    image_list = material['image_list'] if 'image_list' in material else []
    subtitle_list = material['subtitle_list'] if 'subtitle_list' in material else []

    input_config = {
        "video_list": video_list,
        "audio_list": audio_list,
        "image_list": image_list,
        "subtitle_list": subtitle_list
    }

    output_config = {
        "Width": output_width,
        "Height": output_height
    }

    payload = {
        "Prompt": text,
        "Mode": "Modify",
        "InputConfig": json.dumps(input_config),
        "OutputConfig": json.dumps(output_config),
        "BaseTimeline": json.dumps(timeline)
    }

    try:

        response = invoke_api('SubmitTimelineGenerateJob', payload)
        job_id = response['JobId']

        payload = {
            "JobId": job_id
        }

        while True:
            response = invoke_api('GetSmartHandleJob', payload)
            status = response['State']

            if status == 'Finished':
                return response['JobResult']['AiResult']
            elif status == 'Failed':
                return response['ErrorMessage'] if 'ErrorMessage' in response and response['ErrorMessage'] != '' else "Timeline Generate Failed"
            else:
                time.sleep(5)
    except TeaException as te:
        return te.data['Message']
    except Exception as e:
        print(e)
        return "Timeline Generate Failed, Exception Occurred"
