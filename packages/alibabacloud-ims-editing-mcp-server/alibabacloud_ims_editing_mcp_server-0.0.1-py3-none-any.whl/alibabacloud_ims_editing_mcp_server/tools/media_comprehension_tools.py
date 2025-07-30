import json
import logging
from typing import Annotated
from pydantic import Field

from alibabacloud_ice20201109 import models as ice20201109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_ims_editing_mcp_server.tools.tool_registration import *
from alibabacloud_ims_editing_mcp_server.client import ice_client


@register_level_tools(standard_tool, trial_tool, tool_info={
    'tags': {'分析素材阶段', '提交任务', '内容理解'}
})
def submit_media_comprehension_job(media_id_list: Annotated[list, Field(description="媒资Id列表")]) -> list:
    """
    <tags>'分析素材阶段','提交任务','内容理解'</tags>
    <subscriptionLevel>Standard</subscriptionLevel>
    <toolDescription>对输入媒资进行视频内容理解，进行剧情事件分析</toolDescription>
    <return>任务id</return>

    Args:
        media_id_list (list): 视频媒资Id列表
    """
    job_info_list = []
    for media_id in media_id_list:
        job_id = submit_smart_tag_job(media_id)
        job_info_list.append({
            "media_id": media_id,
            "job_id": job_id
        })
    return job_info_list


@register_level_tools(standard_tool, trial_tool, tool_info={
    'tags': {'分析素材阶段', '查询任务', '内容理解'}
})
def get_media_comprehension_job(job_info_list: Annotated[list, Field(description="任务信息列表")]) -> dict:
    """
    <tags>'分析素材阶段','查询任务','内容理解'</tags>
    <subscriptionLevel>Standard</subscriptionLevel>
    <toolDescription>查询内容理解结果，输入job_info_list，并返回任务结果</toolDescription>
    <return>如果任务失败或者还在处理，会返回任务状态，如果任务成功，则会返回视频理解结果，说明任务完成。</return>

    获取查询结果之后，因为查询结果比较多，所以不需要在回答里面罗列，仅展示即可。
    Args:
        job_info_list (list): 任务信息列表，包含以下字段：
            job_id (string): 任务id
            media_id (string): 媒资id
    """
    job_result = {}
    for job_info in job_info_list:
        job_id = job_info["job_id"]
        media_id = job_info["media_id"]
        query_smart_tag_job_request = ice20201109_models.QuerySmarttagJobRequest(
            job_id=job_id
        )
        runtime = util_models.RuntimeOptions()
        result = None
        try:
            resp = ice_client.query_smarttag_job_with_options(query_smart_tag_job_request, runtime)
            logging.info(resp.body)
            job_status = resp.body.job_status
            if job_status == "Success":
                result = resp.body.results.result
                for res in result:
                    if res.type == "EventSplit":
                        job_result[media_id] = {"EventInfoList": json.loads(res.data)}
            elif job_status == "Submitted" or job_status == "Processing":
                job_result[media_id] = f"the job {job_id} is processing"
            else:
                job_result[media_id] = f"the job {job_id} is failed because of " + resp.body.results.result[0].data
        except Exception as error:
            logging.exception(error)
            return str(error)

    return job_result


def submit_smart_tag_job(media_id: str) -> str:
    job_input = ice20201109_models.SubmitSmarttagJobRequestInput(
        type='Media',
        media=media_id
    )
    submit_smart_tag_job_request = ice20201109_models.SubmitSmarttagJobRequest(
        input=job_input,
        template_id='S00000103-000003',
        params='{"clipSplitParams":{"splitType":"event"}}'
    )
    runtime = util_models.RuntimeOptions()
    try:
        resp = ice_client.submit_smarttag_job_with_options(submit_smart_tag_job_request, runtime)
        logging.info(resp.body)
        return resp.body.job_id
    except Exception as error:
        logging.exception(error)
        return str(error)
