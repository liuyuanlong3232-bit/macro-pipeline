#!/usr/bin/env python3
"""双向记忆同步：本地↔GitHub↔VPS"""
import os, sys, subprocess
from pathlib import Path
from datetime import datetime

HOME = Path.home()
REPO = HOME / "hermes-macro-pipeline"
SHARED = REPO / "shared"
SHARED_MEMORIES = SHARED / "memories"
SHARED_SKILLS = SHARED / "skills"

def run(cmd, cwd=REPO):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(cwd))

def git(cmd):
    return run(f"git {cmd}")

def main():
    SHARED_MEMORIES.mkdir(parents=True, exist_ok=True)
    SHARED_SKILLS.mkdir(parents=True, exist_ok=True)

    mode = sys.argv[1] if len(sys.argv) > 1 else "push"

    if mode == "push":
        # 推记忆 + 推技能到GitHub
        print("📤 push: 本地 → GitHub")
        
        # 1. 记忆
        mem_src = HOME / "AppData" / "Local" / "hermes" / "memories" / "MEMORY.md"
        if mem_src.exists():
            content = mem_src.read_text("utf-8")
            (SHARED_MEMORIES / "LOCAL_MEMORY.md").write_text(content, "utf-8")
            print("  记忆已导出")
        
        # 2. 技能（只同步用户自定义的）
        local_skills = HOME / "AppData" / "Local" / "hermes" / "skills"
        if local_skills.exists():
            for skill_dir in local_skills.iterdir():
                if skill_dir.is_dir() and skill_dir.name not in [".git"]:
                    target = SHARED_SKILLS / skill_dir.name
                    run(f'cp -r "{skill_dir}" "{target}"')
            print("  技能已导出")
        
        # 3. Git提交推送
        git("add shared/")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        result = git(f'commit -m "shared: sync memories+skills {ts}"')
        if "nothing to commit" not in result.stdout + result.stderr:
            git("push")
            print("  已推送到GitHub")
        else:
            print("  无变更，跳过commit")
    
    elif mode == "pull":
        # 从GitHub拉VPS的记忆和技能
        print("📥 pull: GitHub → 本地")
        
        git("pull")
        print("  已拉取最新")
        
        # 导入VPS记忆（如果存在）
        vps_mem = SHARED_MEMORIES / "VPS_MEMORY.md"
        if vps_mem.exists():
            import_target = HOME / "AppData" / "Local" / "hermes" / "memories" / "VPS_SYNCED.md"
            import_target.write_text(vps_mem.read_text("utf-8"), "utf-8")
            print("  VPS记忆已导入到本地")
        
        # 导入远程技能
        remote_skills = SHARED_SKILLS
        if remote_skills.exists():
            local_skills = HOME / "AppData" / "Local" / "hermes" / "skills"
            for skill_dir in remote_skills.iterdir():
                if skill_dir.is_dir():
                    target = local_skills / skill_dir.name
                    run(f'cp -r "{skill_dir}" "{target}"')
            print("  技能已导入到本地")
    
    elif mode == "push_vps":
        # VPS专用：推VPS的MEMORY.md到shared/
        print("📤 push_vps: VPS → GitHub")
        
        vps_mem = HOME / "hermes-pipeline" / "memories" / "MEMORY.md"
        if vps_mem.exists():
            content = vps_mem.read_text("utf-8")
            (SHARED_MEMORIES / "VPS_MEMORY.md").write_text(content, "utf-8")
            print("  VPS记忆已导出")
        
        git("add shared/")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        result = git(f'commit -m "shared: vps push {ts}"')
        if "nothing to commit" not in result.stdout + result.stderr:
            git("push")
            print("  已推送到GitHub")
        else:
            print("  无变更")
    
    elif mode == "pull_vps":
        # VPS专用：拉本地记忆到VPS
        print("📥 pull_vps: GitHub → VPS")
        
        git("pull")
        print("  已拉取最新")
        
        local_mem = SHARED_MEMORIES / "LOCAL_MEMORY.md"
        if local_mem.exists():
            import_target = HOME / "hermes-pipeline" / "memories" / "MEMORY.md"
            import_target.write_text(local_mem.read_text("utf-8"), "utf-8")
            print("  本地记忆已导入到VPS Hermes")
        
        # 导入远程技能
        remote_skills = SHARED_SKILLS
        if remote_skills.exists():
            vps_skills = HOME / "hermes-pipeline" / "skills"
            for skill_dir in remote_skills.iterdir():
                if skill_dir.is_dir():
                    target = vps_skills / skill_dir.name
                    run(f'cp -r "{skill_dir}" "{target}"')
            print("  技能已导入到VPS")

if __name__ == "__main__":
    main()
