# Moving the annotation tool to Azure (Azure for Students)

The tool runs today on Khurram's laptop, reached through a Cloudflare tunnel at https://bluecart.khurramshafique.com.
Azure for Students gives 750 hours a month of a **B1s** virtual machine free for 12 months, plus $100 credit for the small disk.
This guide moves the tool to such a VM. **The address stays the same**, and accounts and answers move with it.

Three scripts do the work, in `scripts/azure/`:

| Script | Where it runs | What it does |
|---|---|---|
| `setup_vm.sh` | on the VM | installs Python, Potato 2.9.4, cloudflared, and a service that starts the tool at boot |
| `migrate.sh` | on the laptop | stops the laptop copy, copies the server folder to the VM, starts the tool there |
| `tunnel_vm.sh` | on the VM | gives the VM its own tunnel and points the bluecart address at it |

Plan about 45 minutes. Classmates see an error page between step C and step E (a few minutes), so pick a time when
nobody is labeling (admin page, Annotators tab, Last Activity).

---

## A. Create the VM in the Azure portal (about 10 minutes)

1. portal.azure.com → **Create a resource** → **Virtual machine** → Create.
2. **Basics**
   - Resource group: Create new, `bluecart`
   - Virtual machine name: `bluecart-vm`
   - Region: East US (any US region is fine)
   - Image: **Ubuntu Server 24.04 LTS, x64**
   - Size: **Standard_B1s** (1 vCPU, 1 GiB). If it is not in the short list, click "See all sizes" and search `B1s`. It carries the "free services eligible" label.
   - Authentication type: **SSH public key**. Username: `azureuser`. Key pair name: `bluecart-vm`, "Generate new key pair".
   - Public inbound ports: **SSH (22)** only. The tool needs no open port; the tunnel connects outward.
3. **Disks**: OS disk type **Standard SSD**, 30 GiB. Leave the rest.
4. **Review + create** → Create. When asked, **download the private key** (`bluecart-vm.pem`). It is shown once.
5. After "Your deployment is complete", open the VM and copy its **Public IP address**.

## B. Connect from the laptop and prepare the VM (about 10 minutes)

In Ubuntu (WSL). Replace `20.1.2.3` with the public IP from step A5.

```bash
mkdir -p ~/.ssh && cp "/mnt/c/Users/KhurramShafique/Downloads/bluecart-vm.pem" ~/.ssh/ && chmod 600 ~/.ssh/bluecart-vm.pem
```

Make an SSH shortcut so every later command can say `bluecart-vm`:

```bash
printf '\nHost bluecart-vm\n  HostName 20.1.2.3\n  User azureuser\n  IdentityFile ~/.ssh/bluecart-vm.pem\n' >> ~/.ssh/config
```

Copy the scripts over and run the setup on the VM:

```bash
cd ~/workspace-school/bluecart/blue-cart-check && scp scripts/azure/setup_vm.sh bluecart-vm:/tmp/ && ssh bluecart-vm 'bash /tmp/setup_vm.sh'
```

The last lines say "VM is ready".

## C. Log the VM in to Cloudflare (one time, 2 minutes)

```bash
ssh bluecart-vm 'cloudflared tunnel login'
```

It prints a link. Open it in Chrome on Windows, sign in to Cloudflare, choose **khurramshafique.com**, click Authorize.
The command on the VM then finishes by itself.

## D. Move the tool (about 5 minutes; classmates are offline from here until step E)

On the laptop:

```bash
cd ~/workspace-school/bluecart/blue-cart-check && bash scripts/azure/migrate.sh bluecart-vm
```

It stops the laptop copy, copies `deploy/local_server` (about 85 MB) and starts the tool on the VM.
The last lines should say `tool on the VM answers: 200` and the number of accounts.

## E. Point the address at the VM

```bash
ssh bluecart-vm 'bash /opt/bluecart/tunnel_vm.sh'
```

It creates the tunnel `bluecart-azure`, rewrites the DNS record for bluecart.khurramshafique.com, and starts the tunnel as a
service. The last line should say `https://bluecart.khurramshafique.com answers: 200`. DNS can take a minute to settle.

## F. Check

1. Open https://bluecart.khurramshafique.com in a private window: the login page.
2. Sign in with your own account: your photos and progress are there.
3. Open `/admin` with the key from `deploy/local_server/admin_api_key.txt` (the same file was copied): all annotators listed.
4. On the laptop, `scripts/start_public_tool.sh` is no longer needed. Do not run it while the VM serves the address, or two
   copies would collect answers in two places.

## Later changes

Rebuild the folder on the laptop as before, then copy it again:

```bash
cd ~/workspace-school/bluecart/blue-cart-check && python scripts/make_hf_space.py --out deploy/local_server --no-backup --shared 30 --per-annotator 200 --annotators 10 --labels-per-photo 2 --keep-photo-list && bash scripts/azure/migrate.sh bluecart-vm
```

`migrate.sh` copies the laptop folder over the VM folder, including `annotation_output`. So **before a rebuild, copy the
VM's answers back first**, or the laptop's older answers overwrite the newer ones on the VM:

```bash
rsync -az bluecart-vm:/opt/bluecart/server/annotation_output/ ~/workspace-school/bluecart/blue-cart-check/deploy/local_server/annotation_output/ && rsync -az bluecart-vm:/opt/bluecart/server/user_config.json ~/workspace-school/bluecart/blue-cart-check/deploy/local_server/user_config.json
```

Run that same command any time to fetch the answers for `show_labels.py`, `labeling_time.py` and `compute_agreement.py`.

## Rollback

If anything goes wrong, point the address back at the laptop and restart the laptop copy:

```bash
cloudflared tunnel route dns --overwrite-dns cfde6c21-267a-4feb-9ebf-0065fd179ecf bluecart.khurramshafique.com && cd ~/workspace-school/bluecart/blue-cart-check && bash scripts/start_public_tool.sh
```

(`cfde6c21...` is the laptop's tunnel id, from `~/.cloudflared/config.yml`.)

## Cost and housekeeping

- B1s: 750 hours a month free for 12 months, which is the whole month. Disk: about $2 to $3 a month from the $100 credit.
- Stop (deallocate) the VM in the portal when annotation is over; a stopped VM costs only the disk.
- The VM has no open ports except SSH. Keep the `.pem` file private; it is the only way in.
- Logs on the VM: `journalctl -u bluecart -f` and `journalctl -u cloudflared -f`.
