import os
import git
# import gemini  # Uncomment and configure when integrating Gemini

GENERATED_DIR = os.path.join(os.path.dirname(__file__), 'generated')

class GitHubIntegrationAgent:
    def __init__(self, repo_path=None):
        self.repo_path = repo_path or os.path.dirname(__file__)
        self.repo = git.Repo(self.repo_path)

    def generate_commit_message(self, changed_files):
        """
        Generate a commit message based on the changes using Gemini (stub).
        """
        # response = gemini.generate_commit_message(...)
        return f"Auto-commit: updated {', '.join(changed_files)}"

    def commit_and_push(self, changed_files):
        """
        Commit and push the given files to GitHub with an auto-generated message.
        """
        commit_message = self.generate_commit_message(changed_files)
        self.repo.index.add([os.path.join('generated', f) for f in changed_files])
        self.repo.index.commit(commit_message)
        origin = self.repo.remote(name='origin')
        origin.push()
        print(f"Committed and pushed: {commit_message}") 