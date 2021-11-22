import subprocess
import sys
# The purpose of this script is to add vIOMMU device for Proxmox VM
# NOTE: Changes to VM would not be permanent. The script would need to be run each time vIOMMU device is needed.
# Python 3.5 or higher is required for this script to run.

def add_iommu_option(vmid):
    # Get the 'qm showcmd' output and break down into a list
    vmcommand_options_list = subprocess.run(['/usr/sbin/qm', 'showcmd', str(vmid)], stdout=subprocess.PIPE).stdout.decode('utf-8').split()

    # Add the vIOMMU feature to the VM options
    first_device_option_index = vmcommand_options_list.index("-device")
    vmcommand_options_list.insert(first_device_option_index, "'intel-iommu,intremap=on,caching-mode=on'")
    vmcommand_options_list.insert(first_device_option_index, "-device")
    vmcommand_options_list.append("-machine")
    vmcommand_options_list.append("'accel=kvm,kernel-irqchip=split'")

    # Run the VM. Options are now shown in `ps auxxx | sed 's,^.*/usr/bin/kvm,/usr/bin/kvm,' | head -n-3 | grep -e "-id <YOUR-VM-ID>"` command
    new_vmprocess = subprocess.run(" ".join(vmcommand_options_list), shell=True, check=True)

def main():
    try:
        if not len(sys.argv) == 2:
            # Only 1 argument is allowed
            raise IndexError
        elif not sys.argv[1].isnumeric():
            # Only numerical argument value is allowed
            raise ValueError    
        else:
            # Wait for VM to shutdown either gracefully or forcefully by user before adding options
            vm_id = sys.argv[1]
            subprocess.run(["/usr/sbin/qm", "wait", str(vm_id)], check=True)
            add_iommu_option(vm_id)
    except IndexError:
        print("At least a numerical argument value is needed and only 1 argument can be used")
        sys.exit()
    except ValueError:
        print("Argument needs to be a number")
        sys.exit()
    except subprocess.CalledProcessError:
        # No such VM ID exists. `qm` command would output errors
        sys.exit()
    except FileNotFoundError:
        print("'/usr/sbin/qm' file path not present. Exiting...")
        sys.exit()

if __name__ == "__main__":
    main()
