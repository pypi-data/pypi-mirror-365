import argparse
import asyncio
import os
import csv

import surfari.config as config
from surfari.site_credential_manager import SiteCredentialManager
from surfari.cdp_browser import ChromiumManager
from surfari.tools.navigation_tool import NavigationTool

import surfari.surfari_logger as surfari_logger
logger = surfari_logger.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Run Surfari navigation task")
    parser.add_argument("-t", "--task_goal", help="The user task to accomplish (ignored if --batch_file is used)")
    parser.add_argument("-u", "--url", help="The URL to navigate to")
    parser.add_argument("-n", "--site_name", help="Optional site name")
    parser.add_argument("-b", "--use_system_chrome", action="store_true", help="Use system-installed Chrome")
    parser.add_argument("-l", "--llm_model", help="Override default LLM model (e.g. llama3:8b, gpt-4)")
    parser.add_argument("-s", "--mask_sensitive_info", action="store_true", help="Mask sensitive info")
    parser.add_argument("-m", "--multi_action_per_turn", action="store_true", help="Allow multiple actions per turn")
    parser.add_argument("-U", "--username", help="Username to save for the site (used with --password)")
    parser.add_argument("-P", "--password", help="Password to save for the site (used with --username)")
    parser.add_argument("-f", "--batch_file", help="Path to CSV batch file with columns: task_goal,site_name,url,username,password,mask_sensitive_info,multi_action_per_turn")
    return parser.parse_args()


async def run_single_task(
    task_goal,
    site_name=None,
    url=None,
    model=None,
    mask_sensitive_info=False,
    multi_action_per_turn=False,
    username=None,
    password=None,
    use_system_chrome=False
):
    try:
        if username and password and site_name and url:
            cred_manager = SiteCredentialManager()
            cred_manager.save_credentials(site_name=site_name, url=url, username=username, password=password)
            logger.info(f"[{site_name}] Credentials saved")

        manager = await ChromiumManager.get_instance(use_system_chrome=use_system_chrome)
        page = await manager.get_new_page()

        nav_tool = NavigationTool(
            model=model,
            site_name=site_name,
            url=url,
            mask_sensitive_info=mask_sensitive_info,
            multi_action_per_turn=multi_action_per_turn,
        )
        result = await nav_tool.navigate(page, task_goal=task_goal)
        logger.info(f"[{site_name or url}] Final answer: {result}")
    except Exception as e:
        logger.exception(f"[{site_name or url}] Error during navigation")
    finally:
        try:
            await page.close()
        except Exception:
            pass


async def run_batch_csv(csv_path, model, use_system_chrome):
    tasks = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, 1):
            try:
                task_goal = row.get("task_goal", "").strip() or None
                if task_goal.startswith("#") or not task_goal:
                    logger.info(f"[Line {line_num}] Skipped: empty or comment task_goal")
                    continue
                site_name = row.get("site_name", "").strip() or None
                url = row.get("url", "").strip() or None
                username = row.get("username", "").strip() or None
                password = row.get("password", "").strip() or None
                mask_flag = row.get("mask_sensitive_info", "").strip().lower()
                mask_sensitive_info = mask_flag in ("1", "true", "yes")

                multi_action_flag = row.get("multi_action_per_turn", "").strip().lower()
                multi_action_per_turn = multi_action_flag in ("1", "true", "yes")
                
                if not task_goal:
                    logger.warning(f"[Line {line_num}] Skipped: task_goal is required")
                    continue

                logger.info(f"[Line {line_num}] Task: {task_goal} | Site: {site_name} | URL: {url}")

                kwargs = {
                    "task_goal": task_goal,
                    "site_name": site_name,
                    "url": url,
                    "model": model,
                    "mask_sensitive_info": mask_sensitive_info,
                    "multi_action_per_turn": multi_action_per_turn,
                    "use_system_chrome": use_system_chrome,
                }
                if username:
                    kwargs["username"] = username
                if password:
                    kwargs["password"] = password

                tasks.append(run_single_task(**kwargs))

            except Exception as e:
                logger.exception(f"[Line {line_num}] Error parsing CSV row: {row}")

    await asyncio.gather(*tasks)


async def main():
    args = parse_args()

    if args.llm_model:
        config.CONFIG["app"]["llm_model"] = args.llm_model
        logger.info(f"Using custom LLM model: {args.llm_model}")

    if args.batch_file:
        if not os.path.isfile(args.batch_file):
            raise FileNotFoundError(f"Batch file not found: {args.batch_file}")
        await run_batch_csv(
            csv_path=args.batch_file,
            model=args.llm_model,
            use_system_chrome=args.use_system_chrome,
        )
    else:
        if not args.task_goal:
            raise ValueError("Missing required argument: --task_goal (when not using --batch_file)")

        await run_single_task(
            task_goal=args.task_goal,
            site_name=args.site_name,
            url=args.url,
            model=args.llm_model,
            mask_sensitive_info=args.mask_sensitive_info,
            multi_action_per_turn=args.multi_action_per_turn,
            username=args.username,
            password=args.password,
            use_system_chrome=args.use_system_chrome,
        )

    if ChromiumManager._instance:
        await ChromiumManager._instance.stop()


if __name__ == "__main__":
    asyncio.run(main())
