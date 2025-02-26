# SafeArena Environment Setup

Setup scripts for SafeArena.

## Step 1: Initial setup

First, make sure to be in the correct dir and create a symlink to the `containers/` dir:
```sh
git clone https://github.com/McGill-NLP/safearena
cd safearena/env-setup

# Change this to the location of the containers folder (if you have it)
ORIGINAL_CONTAINERS_DIR=~/scratch/webarena/containers

# create a symlink to the containers folder
ln -s $ORIGINAL_CONTAINERS_DIR containers
```

## Step 1.1: Get the files


> [!WARNING]
> This section should be skipped if the files are already present in the `containers/` folder.

Download the necessary docker images from the [official Webarena repo](https://github.com/web-arena-x/webarena/tree/main/environment_docker), or using these [unofficial instructions](https://github.com/gasse/webarena-setup/tree/main/webarena). You'll need the following files (download them to `containers` dir so it uses the "scratch" folder):
- `shopping_final_0712.tar`
- `wikipedia_en_all_maxi_2022-05.zim`

Then, download the following files from [`McGill-NLP/safearena-environments`](https://huggingface.co/datasets/McGill-NLP/safearena-environments):
- `safearena_shopping_admin.tar.gz` (sha256sum: `82d136ad1a6d0db9e4a398ca9f38d9956cfbfb076d9ff84dddd32e0227628822`)
- `safearena_forum.tar.gz` (sha256sum: `186490daed7f66512d9a7f5dd088c78d8dfc0f2c4890a6681d4424440372d321`)
- `safearena_gitlab.tar.gz` (sha256sum: `26b773ff60ec4663c75dc9c0d8630b28da58c1e527d4b92a8fa6fe3a089256c8`)

### Downloading SafeArena containers

To download them, you will need to first have access to `McGill-NLP/safearena-environments` (request access if needed). Then, you will need to install `huggingface_hub` and authenticate with `huggingface-cli`:

```bash
pip install huggingface-hub
huggingface-cli login
```

Now, run in python:

```python
import os
from huggingface_hub import snapshot_download

archive_location = os.environ.get("ARCHIVES_LOCATION", "./containers")

# Download the containers from the huggingface repo
snapshot_download(
    repo_id="McGill-NLP/safearena-environments", 
    repo_type="dataset", 
    local_dir=os.path.join(archive_location, "downloads"),
)
```

Now, move `safearena_shopping_admin.tar.gz` from `$ARCHIVES_LOCATION/downloads` to `$ARCHIVES_LOCATION` and extract it:

```bash
mv $ARCHIVES_LOCATION/downloads/safearena_shopping_admin.tar.gz
```

Finally, assemble the parts `aa`, `ab`, etc. of the two other containers into `$ARCHIVES_LOCATION`:

```bash
cat $ARCHIVES_LOCATION/downloads/safearena_forum.tar.gz.* > $ARCHIVES_LOCATION/safearena_forum.tar.gz
cat $ARCHIVES_LOCATION/downloads/safearena_gitlab.tar.gz.* > $ARCHIVES_LOCATION/safearena_gitlab.tar.gz
```

> [!NOTE] If you're planning to setup multiple instances, you should download these files once in a shared location. Then, you can mount this shared location to the `containers` folder in each instance.


## Step 2: Configure the scripts

```bash
# Port: uupia
# uu: two-digit user number, e.g. 20 -> john doe (jod), 21 -> jane doe (jad)
# p: project number, e.g. 0 -> safearena, 1 -> visualwebarena, etc.
# i: instance number, e.g. 0 -> instance for experiment #1, 1 -> instance for experiment #2, ...
# a: application number, e.g. 0 -> homepage, 1 -> shopping, 2 -> classifieds, 3 -> reddit, 4 -> wikipedia, ...

USER_INITIAL="aa"
USER_NUM=20
INSTANCE_NUM=0
PROJECT_NUM=0
```

> [!IMPORTANT]
> You MUST edit `00_vars.sh`! The default values are placeholders and will not work.

In `00_vars.sh`, you should set the following variables:

- `ARCHIVES_LOCATION`: the location of the `containers` symlinked directory. You should always use absolute paths.
- `USER_INITIAL`: the initial user number. 
- `USER_NUM`: two-digit user number, e.g. 20 -> john doe (jod), 21 -> jane doe (jad), etc.
- `INSTANCE_NUM`: the instance number. e.g. 0 -> instance for experiment #1, 1 -> instance for experiment #2, ...
- `PROJECT_NUM`: the project number. e.g. 0 -> safearena, 1 -> visualwebarena, etc.
- `PUBLIC_HOSTNAME`: the public hostname of the server. This is used to generate the URLs for the different services.
- `CF_DOMAIN`: the cloudflare domain. This is used to generate the URLs for the different services.

## Step 3: Extract / load the image files (very long, do it just once)

Load the docker image files
```sh
bash 01_docker_load_images.sh
```

Once these three steps are completed, you can get rid of the downloaded files (or unmount your shared folder) as these won't be needed any more.

## Step 4: Setting up the containers and running the server (cloudflare edition)


### Setting up Cloudflared

> [!NOTE]
> The clouflare setup is useful if you want to access the instance from outside the internal network. Otherwise, it is optional and you can skip this section.

First, install cloudflared:
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

mkdir ~/path_scripts
mv cloudflared-linux-amd64 ~/path_scripts/cloudflared
chmod +x ~/path_scripts/cloudflared
```

add the following to your `~/.bashrc` or `~/.bash_profile`:
```bash
# add cloudflared to path
export PATH=$PATH:$HOME/path_scripts/
```

If that worked, you should now be able to run `cloudflared` from the terminal, e.g.

```bash
cd /path/to/safearena/env-setup

cloudflared --version
```

Next, login to cloudflare and get your API token:

```bash
# login to cloudflare
cloudflared login
```

> [!NOTE]
> You need to be an administrator to login via CLI, which you need a *Super Administrator* to add you. Once you are logged in, you can be downgraded from admin, as you only need the following permissions (for *All Domains*):
> - HTTP Applications: Can view and edit HTTP Applications
> - Cloudflare Zero Trust: Can edit Cloudflare Zero Trust.
> - DNS: Can edit DNS records.
> - Cloudflare Access: Can edit Cloudflare Access.
> - Analytics: Can read Analytics.

### Setting up the containers

> [!NOTE]
> At this point, you will need to know what `screen` is. If you don't know what it is, you can read more about it [here](https://linuxize.com/post/how-to-use-linux-screen/). Cheat sheets, [like this one](https://gist.github.com/jctosta/af918e1618682638aa82), can be helpful as well. You can also use `tmux` if you prefer, but the instructions below are for `screen` so you will need to adapt them.


Similar to the previous setup, we can use a screen session, then run scripts 02 to 06 in order. The last script serves the homepage and should stay up. The only difference is that we use `05cf` instead of `05` to patch the containers.

```bash
# Optional: you can set the instance number with CUSTOM_INSTANCE_NUM if you want to run multiple instances at the same time. By default, it'll be 0
export CUSTOM_INSTANCE_NUM=1

# If you want to use the cloudflare tunnel, set this to true
export HOST_WITH_CLOUDFLARE="true"

bash 02_docker_remove_containers.sh
bash 03_docker_create_containers.sh
bash 04_docker_start_containers.sh
bash 05_docker_patch_containers.sh
```

Now, we need to serve the homepage and the reset server. We will use the `06_serve_homepage.sh` and `07_serve_reset.sh` scripts to do that:

```bash
# for env-setup/reset_server/reset.sh to know if it should use cloudflared
export HOST_WITH_CLOUDFLARE="true"

# you want to start a new screen here, e.g. screen -S server-$HOMEPAGE_CF_NAME, then run above commands
bash 06_serve_homepage.sh

# in a separate screen, e.g. screen -S server-$RESET_CF_NAME
bash 07_serve_reset.sh
```

If you want to boot them as background processes, you can directly use a command to create a `screen` and run the script in it all in one line:

```bash
# optional: you can set the instance number with CUSTOM_INSTANCE_NUM if you want to run multiple instances at the same time
export CUSTOM_INSTANCE_NUM=1
export HOST_WITH_CLOUDFLARE="true"
source 00_vars.sh

screen -S server-$HOMEPAGE_CF_NAME -dm bash 06_serve_homepage.sh
screen -S server-$RESET_CF_NAME -dm bash 07_serve_reset.sh
```

and kill the screens with:

```bash
export CUSTOM_INSTANCE_NUM=1
export HOST_WITH_CLOUDFLARE="true"
source 00_vars.sh

screen -S server-$HOMEPAGE_CF_NAME -X quit
screen -S server-$RESET_CF_NAME -X quit
```

### Tunnel the instance

Run the following command to tunnel the instance:

```bash
export CUSTOM_INSTANCE_NUM=1
export HOST_WITH_CLOUDFLARE="true"

# make sure you are in env-setup/ dir
source 00_vars.sh

screen -S cf-$HOMEPAGE_CF_NAME -dm bash create_and_run_tunnel.sh $HOMEPAGE_CF_NAME $HOMEPAGE_PORT
screen -S cf-$SHOPPING_CF_NAME -dm bash create_and_run_tunnel.sh $SHOPPING_CF_NAME $SHOPPING_PORT
screen -S cf-$SHOPPING_ADMIN_CF_NAME -dm bash create_and_run_tunnel.sh $SHOPPING_ADMIN_CF_NAME $SHOPPING_ADMIN_PORT
screen -S cf-$FORUM_CF_NAME -dm bash create_and_run_tunnel.sh $FORUM_CF_NAME $REDDIT_PORT
screen -S cf-$GITLAB_CF_NAME -dm bash create_and_run_tunnel.sh $GITLAB_CF_NAME $GITLAB_PORT
screen -S cf-$WIKIPEDIA_CF_NAME -dm bash create_and_run_tunnel.sh $WIKIPEDIA_CF_NAME $WIKIPEDIA_PORT
screen -S cf-$RESET_CF_NAME -dm bash create_and_run_tunnel.sh $RESET_CF_NAME $RESET_PORT
```

If you want to kill the tunnels, you can run the following command:
```bash
export CUSTOM_INSTANCE_NUM=1
export HOST_WITH_CLOUDFLARE="true"
source 00_vars.sh

screen -S cf-$HOMEPAGE_CF_NAME -X quit
screen -S cf-$SHOPPING_CF_NAME -X quit
screen -S cf-$SHOPPING_ADMIN_CF_NAME -X quit
screen -S cf-$FORUM_CF_NAME -X quit
screen -S cf-$GITLAB_CF_NAME -X quit
screen -S cf-$WIKIPEDIA_CF_NAME -X quit
screen -S cf-$RESET_CF_NAME -X quit
```

## Step 5: Sanity check

Go to the homepage and click each link to make sure the websites are operational (some might take ~10 secs to load the first time).

## Step 6: Reset

After an agent is evaluated on SafeArena, a reset is required before another agent can be evaluated.

Run scripts 02 to 06 again, or query the reset URL `http://${PUBLIC_HOSTNAME}:${RESET_PORT}/reset` if the reset server is running.

## Step 7: Exporting the correct env vars for experiments in browsergym

### Cloudflare

You need to use to export those env vars before running the experiments:
```bash
export WA_HOMEPAGE="https://wa-homepage-${SUFFIX}.your-domain.com"
export WA_SHOPPING="https://wa-shopping-${SUFFIX}.your-domain.com/"
export WA_SHOPPING_ADMIN="https://wa-shopping-admin-${SUFFIX}.your-domain.com/admin"
export WA_REDDIT="https://wa-forum-${SUFFIX}.your-domain.com"
export WA_GITLAB="https://wa-gitlab-${SUFFIX}.your-domain.com"
export WA_WIKIPEDIA="https://wa-wikipedia-${SUFFIX}.your-domain.com/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
export WA_FULL_RESET="https://wa-reset-${SUFFIX}.your-domain.com"

# Now, you can run your script for agentlab/browsergym experiments
python my_agentlab_agent_run.py
```

> [!WARNING]
> Do NOT use the env vars `HOMEPAGE_URL`, `REDDIT_URL`, etc. from `00_vars.sh` in your agentlab/browsergym experiments! Those are specific for the setup and should not be used in the experiments, as it may cause issues during evaluation.
> Instead, use the env vars `WA_HOMEPAGE`, `WA_REDDIT`, etc. as shown above.

### Manual

Please export the same env vars based on localhost, and the ports created in 00_vars.sh.

# Acknowlegement

This setup is based on the official WebArena setup scripts. For the official instructions, refer to [WebArena](https://github.com/web-arena-x/webarena/tree/main/environment_docker).

The original implementation of this setup workflow was created by @gasse in the [webarena-setup](https://github.com/gasse/webarena-setup/) repository.