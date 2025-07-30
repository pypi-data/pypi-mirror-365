import json
import logging

from alibabacloud_ice20201109 import models as ice20201109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_ims_editing_mcp_server.tools.tool_registration import *
from alibabacloud_ims_editing_mcp_server.client import ice_client
from alibabacloud_ims_editing_mcp_server.tools.param_type import *

@register_level_tools(basic_tool, trial_tool, tool_info={
    'tags': {'素材预处理阶段', '提交任务'}
})
def register_editing_media(media_type: Annotated[str,Field(description="媒资类型，可选值：video(视频), audio（音频）, image（图片），text(文本)")],
                           input_url: Annotated[str,Field(description="媒资url")],
                           title: Annotated[Optional[str],Field(description="媒资标题")] = None) -> str:
    """
    <tags>'素材预处理阶段','提交任务'</tags>
    <subscriptionLevel>Basic</subscriptionLevel>
    <toolDescription>该工具主要是将输入的源文件input_url注册到IMS的媒资库中</toolDescription>
    <return>媒资id</return>
    """

    register_media_request = ice20201109_models.RegisterMediaInfoRequest(
        input_url=input_url,
        media_type=media_type,
        title=title,
        overwrite=True
    )
    register_media_response = ice_client.register_media_info(register_media_request)
    logging.info(register_media_response.body)
    media_id = register_media_response.body.media_id
    return media_id


@register_level_tools(basic_tool, trial_tool, tool_info={
    'tags': {'素材预处理阶段', '查询任务'}
})
def get_editing_media_info(media_id: Annotated[str,Field(description="媒资id")]) -> str:
    """
    <tags>'素材预处理阶段','查询任务'</tags>
    <subscriptionLevel>Basic</subscriptionLevel>
    <toolDescription>根据媒资ID，查询对应媒资的信息，包含媒资状态、标题、描述等基础信息，也包含源文件url、时长、宽高等文件信息。媒资状态是Normal时，才表述媒资已完成注册，可以被使用。</toolDescription>
    <return>
        media_info_str (string): 媒资信息，是个JSON 字符串，转化成JSON Object后包含以下字段
            status (string): 媒资状态，取值：Normal(正常)/Preparing(准备中)/PrepareFailed(准备失败)/Uploading(上传中)/UploadSucc(上传成功)/UploadFailed(上传失败)
            title (string): 媒资标题
            file_url (string): 源文件地址，当媒资状态为Normal会返回。
            duration (string): 文件时长，单位秒。当媒资状态为Normal会返回
            width (string): 文件宽度，单位：像素。当媒资状态为Normal会返回
            height (string): 文件高度，单位：像素。当媒资状态为Normal会返回
    </return>
    """
    get_media_info_request = ice20201109_models.GetMediaInfoRequest(
        media_id=media_id
    )
    get_media_info_response = ice_client.get_media_info(get_media_info_request)
    logging.info(get_media_info_response.body)
    status = get_media_info_response.body.media_info.media_basic_info.status
    ret = {
        "status": status,
        "title": get_media_info_response.body.media_info.media_basic_info.title
    }
    if status == "Normal":
        file_info_list = get_media_info_response.body.media_info.file_info_list
        if file_info_list and len(file_info_list) > 0:
            for file_info in file_info_list:
                file_basic_info = file_info.file_basic_info
                if file_basic_info.file_type == "source_file":
                    ret["file_url"] = file_basic_info.file_url
                    ret["duration"] = file_basic_info.duration
                    ret["width"] = file_basic_info.width
                    ret["height"] = file_basic_info.height

    return json.dumps(ret, ensure_ascii=False)


@register_level_tools(premium_tool, tool_info={
    'tags': {'获取素材阶段'}
})
def search_editing_media(text: Annotated[str,Field(description="搜索词")]) -> str:
    """
    <tags>'获取素材阶段','搜索视频'</tags>
    <subscriptionLevel>Premium</subscriptionLevel>
    <toolDescription>根据输入的搜索词text，搜索相应搜索库中有关的视频信息。如果有多个搜索词，最好分开多次进行搜索后，汇总搜索结果比较好</toolDescription>
    <return>返回相关视频信息列表，包含MediaId和ClipInfo等。</return>
    """

    result = search_media_by_multimodel(text)
    return result


def search_media_by_multimodel(text: str) -> str:
    search_media_by_multimodal_request = ice20201109_models.SearchMediaByMultimodalRequest(
        text=text
    )
    runtime = util_models.RuntimeOptions()
    try:
        resp = ice_client.search_media_by_multimodal_with_options(search_media_by_multimodal_request, runtime)
        print(resp.body)
        dict_list = [item.to_map() for item in resp.body.media_list]
        json_str = json.dumps(dict_list, ensure_ascii=False)
        return json_str
    except Exception as error:
        print(error)
        return str(error)
