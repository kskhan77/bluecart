# Hosting the annotation tool on Hugging Face

With packs, every annotator installs and runs the tool on their own computer.
With a Hugging Face **Space**, the tool runs once on the internet and annotators only open a link.

**Status (Oct 5, 2026):** the Space folder builds and was tested on this computer with six simulated annotators.
It has **not** been run on Hugging Face yet. The Docker build, the answer backup and the published Potato image are untested there.
Hosting is optional for Phase 1a. The zip packs still work.

---

## Read this first

| Fact | What it means for us |
|---|---|
| **A Docker Space needs a paid plan.** Hugging Face's documentation says Gradio and Docker Spaces "require a paid plan to create: PRO for personal accounts". Potato runs as a Docker Space. | One team member needs a PRO account. Check the price at https://huggingface.co/pricing before starting. |
| **A Space forgets its files on every restart.** It restarts on each `git push`, and after it has slept from being unused. | Answers are copied to a private **Dataset** every 5 minutes. The Dataset is where the answers really live. |
| **A restart also forgets accounts and progress.** | Ask annotators to finish in one sitting. Never push while someone is labeling. |
| **Only the first 10 accounts get the shared photos** (the `--annotators` number). | Give the link only to the assigned annotators. Do not create test accounts on the live Space after it is ready. |
| **The Space repository contains all the photos.** | Use "Protected" visibility: the files stay private and the tool is still reachable by link. Settle the RealWaste license question in `LICENSE.md` first. |

---

## How git fits in

There are **two** git repositories:

| Repository | Where it goes | What is in it |
|---|---|---|
| The project (`blue-cart-check/`) | **GitHub** | Code, guidelines, manifest, docs. This is the link for Canvas. |
| The Space folder (`deploy/hf_space/`) | **Hugging Face** | Only what the tool needs to run: config, welcome page, photos. Built by a script. |

The project ignores `deploy/`, so the two never mix. You do not "pull on Hugging Face".
You **push** the Space folder to Hugging Face with git, and Hugging Face rebuilds and restarts the tool by itself after every push.

---

## Part A: one-time setup on the Hugging Face website

1. **Account.** Create or log in at https://huggingface.co and upgrade to **PRO**.
2. **Access token.** Settings → Access Tokens → New token → type **Write**. Copy it. You will use it as the git password and as a secret.
3. **Dataset for the answers.** New → Dataset → name `blue-cart-check-annotations` → **Private** → Create.
4. **Space for the tool.** New → Space → name `blue-cart-check` → SDK **Docker** → template **Blank** → hardware **CPU basic** → visibility **Protected** → Create.
5. **Secrets.** In the Space: Settings → Variables and secrets → New secret. Add three:

   | Secret name | Value |
   |---|---|
   | `HF_TOKEN` | the Write token from step 2 (lets the tool save answers to the Dataset) |
   | `POTATO_SECRET_KEY` | any long random text (keeps logins valid) |
   | `POTATO_ADMIN_API_KEY` | another long random text (the password for the `/admin` page) |

   To make random text in Ubuntu:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

Below, `YOURNAME` means your Hugging Face username.

## Part B: build the Space folder

From the project folder, with the environment on:

```bash
cd ~/workspace-school/bluecart/blue-cart-check
source .venv/bin/activate
python scripts/make_hf_space.py --backup-repo YOURNAME/blue-cart-check-annotations
```

Defaults: 30 shared photos, 120 photos per annotator, 6 annotators, 1 label per photo. Our live setting is `--per-annotator 200 --annotators 10 --labels-per-photo 2` (every photo labeled by two people, see README §6). Change them with `--shared`, `--per-annotator`, `--annotators` and `--labels-per-photo`.
The script prints a warning while the guidelines still have the team to-do box.

## Part C: push it to Hugging Face with git

First time only:

```bash
cd ~/workspace-school/bluecart/blue-cart-check/deploy/hf_space
git init -b main
git remote add space https://huggingface.co/spaces/YOURNAME/blue-cart-check
git add -A
git commit -m "Blue Cart Check annotation tool"
git push --force space main
```

Git asks for a username and a password. The username is your Hugging Face name. The password is the **access token**, not your account password.
`--force` is needed only on this first push, because the new Space already holds a starter file.

Then open the Space page. It shows **Building**, then **Running**. The tool is at:

```
https://YOURNAME-blue-cart-check.hf.space
```

## Part D: check it before anyone uses it

1. Open the link, choose the **Register** tab, make an account, read the welcome page, label two photos.
2. Wait about 5 minutes and open the Dataset page. New files should appear. **If nothing appears, the backup is not working and answers would be lost. Do not send the link out.**
3. Open `https://YOURNAME-blue-cart-check.hf.space/admin` and paste the `POTATO_ADMIN_API_KEY` value. You should see your test account.
4. **Reset before the real run.** Your test account used up one of the 6 places for the shared photos. In the Space: Settings → **Factory rebuild**. That wipes the test account. The test answers stay in the Dataset under your test name. Ignore them later.

## Part E: the real run

Send each annotator the link and this text:

> Open the link, choose **Register**, use your UM uniqname and any password. Read the welcome page and label for about one hour **in one sitting**. Nothing to install and nothing to send back.

While people are labeling: do not push, do not rebuild, do not change settings.

## Part F: get the answers

```bash
cd ~/workspace-school/bluecart/blue-cart-check
git clone https://huggingface.co/datasets/YOURNAME/blue-cart-check-annotations annotation/returned/hf_space
python scripts/show_labels.py
python scripts/labeling_time.py
```

Later, to fetch new answers: `cd annotation/returned/hf_space && git pull`.
`annotation/returned/` is ignored by the project's git, so answers and names never go to GitHub by accident.

## Part G: change something later

1. Change it in the project (guidelines, config, photos).
2. Run `python scripts/make_hf_space.py --backup-repo YOURNAME/blue-cart-check-annotations` again. It keeps the Space folder's git history.
3. Push:
   ```bash
   cd deploy/hf_space
   git add -A
   git commit -m "Update tool"
   git push space main
   ```

Every push restarts the Space and wipes its accounts and progress. Only push when nobody is labeling.

## Part H: the project itself on GitHub

Create an **empty** repository on github.com named `blue-cart-check`, then:

```bash
cd ~/workspace-school/bluecart/blue-cart-check
git add -A
git commit -m "Phase 1a: data, guidelines, annotation tool"
git remote add origin https://github.com/YOUR-GITHUB-NAME/blue-cart-check.git
git push -u origin main
```

Raw photos (`data/raw/`), packs, returned answers and the Space folder are ignored and are not uploaded.
Add Daud, Hina and Ian under Settings → Collaborators.

---

## If something goes wrong

| Problem | What to try |
|---|---|
| Creating the Space says a paid plan is required | The account is not PRO yet |
| `git push` is rejected because of large or binary files | Every file must be under 10 MB (ours are). If Hugging Face still asks for it, install Git LFS, run `git lfs install` and `git lfs track "*.jpg"`, then commit and push again |
| The Space stays on "Building" or shows an error | Open the **Logs** tab on the Space page. The Dockerfile uses Potato's published image with the tag `latest`. Our config was tested with Potato 2.9.4 |
| The link opens but photos do not load | Check that `media/` was pushed: the Space's Files tab should list the JPEGs |
| No files appear in the Dataset | Check the `HF_TOKEN` secret (it must be a Write token) and the name after `--backup-repo` |
| An annotator sees fewer photos than `--per-annotator` | The list is used up: enough people have already labeled, or `--annotators` was too small. Rebuild with the right numbers, or raise that person's cap with the + button on the admin Annotators tab |

## Another way: one command

Potato can create the Space, the Dataset and the secrets by itself:

```bash
pip install 'potato-annotation[huggingface]'
potato deploy up deploy/hf_space/config.yaml --provider huggingface
```

It asks for your token and shows a plan before doing anything. We have not tried it. The git steps above do the same thing by hand, so you can see each step.
