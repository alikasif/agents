import os
import git
from openai import OpenAI

GENERATED_DIR = os.path.join(os.path.dirname(__file__), 'generated')

class GitHubIntegrationAgent:
    def __init__(self, repo_path=None, remote_url=None):
        self.repo_path = repo_path or os.path.dirname(__file__)
        self.remote_url = remote_url
        self.repo = git.Repo(self.repo_path)
        self.llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if self.remote_url:
            self._ensure_remote()

    def _ensure_remote(self):
        """
        Ensure the remote named 'origin' points to the provided remote_url.
        """
        try:
            if 'origin' in [remote.name for remote in self.repo.remotes]:
                self.repo.delete_remote('origin')
            self.repo.create_remote('origin', self.remote_url)
        except Exception:
            # If remote exists, set its URL
            self.repo.git.remote('set-url', 'origin', self.remote_url)

    def commit_and_push(self, changed_files, remote_url=None):
        """
        Add, commit, and push the given files to the remote repo using gitpython.
        If remote_url is not set, prompt the user for it.
        """
        if remote_url:
            self.remote_url = remote_url
        if not self.remote_url:
            self.remote_url = input('Enter the remote repository URL: ').strip()
        self._ensure_remote()
        # Stage files
        self.repo.index.add([os.path.join('generated', f) for f in changed_files])
        # Generate a commit message
        commit_message = self.generate_commit_message(changed_files)
        self.repo.index.commit(commit_message)
        # Push to remote
        origin = self.repo.remote(name='origin')
        origin.push()
        print(f"Committed and pushed: {commit_message}")

    def generate_commit_message(self, changed_files):
        """
        Use LLM to generate a short, understandable commit message based on the changed files.
        """
        system_prompt = (
            "You are an expert software engineer. Given a list of changed files, generate a short, clear, and understandable git commit message. "
            "The message should summarize the changes in a way that is helpful for future readers. Do not include file names or explanations, just the concise commit message."
        )
        user_prompt = f"Changed files: {', '.join(changed_files)}"
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=50,
                temperature=0.2
            )
            commit_message = response.choices[0].message.content.strip()
            return commit_message
        except Exception as e:
            return f"Update: {', '.join(changed_files)}" 