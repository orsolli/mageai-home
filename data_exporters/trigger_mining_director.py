from mage_ai.orchestration.triggers.api import trigger_pipeline
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
from mage_ai.settings.platform import project_platform_activated
from mage_ai.settings.repo import get_repo_path
from mage_ai.data_preparation.models.triggers import ScheduleStatus, ScheduleType, ScheduleInterval
from datetime import datetime, timedelta

from mage_ai.api.resources.PipelineScheduleResource import PipelineScheduleResource
from mage_ai.data_preparation.models.pipeline import Pipeline
from mage_ai.orchestration.db.models.schedules import PipelineRun, PipelineSchedule

@data_exporter
def trigger(data, *args, **kwargs):
    """
    Trigger another pipeline to run.

    Documentation: https://docs.mage.ai/orchestration/triggers/trigger-pipeline
    """
    is_on = data['is_on'].iloc[0]
    start_time = data['next_change'].iloc[0]

    pipeline_uuid = kwargs["pipeline_uuid"]
    schedule_name = kwargs.get("trigger_name","Is on")
    schedule_name_off = "off".join(schedule_name.split("on"))
    schedule_name_on = "on".join(schedule_name.split("off"))
    if schedule_name_on == schedule_name_off:
        schedule_name_on += " is on"
        schedule_name_off += " is off"
    if is_on:
        schedule_name_new = schedule_name_on
    else:
        schedule_name_new = schedule_name_off

    schedule_type = ScheduleType.TIME
    old_pipeline_schedule = PipelineSchedule.repo_query.filter(
        PipelineSchedule.name == schedule_name,
        PipelineSchedule.pipeline_uuid == pipeline_uuid,
        PipelineSchedule.schedule_type == schedule_type,
    ).first()

    if schedule_name != schedule_name_new:
        old_pipeline_schedule.update(
            status=ScheduleStatus.INACTIVE,
        )

    pipeline_schedule = PipelineSchedule.repo_query.filter(
        PipelineSchedule.name == schedule_name_new,
        PipelineSchedule.pipeline_uuid == pipeline_uuid,
        PipelineSchedule.schedule_type == schedule_type,
    ).first() or PipelineScheduleResource.create(
        dict(
            variables=old_pipeline_schedule.variables,
            description=old_pipeline_schedule.description,
            name=schedule_name_new,
            schedule_type=schedule_type,
            schedule_interval=ScheduleInterval.ALWAYS_ON,
            start_time=start_time,
            status=ScheduleStatus.ACTIVE,
        ),
        None,
        parent_model=Pipeline.get(
            pipeline_uuid,
            all_projects=project_platform_activated(),
        ),
    ).model

    pipeline_schedule.update(
        status=ScheduleStatus.ACTIVE,
        variables=old_pipeline_schedule.variables if old_pipeline_schedule else pipeline_schedule.variables,
        start_time=start_time
    )