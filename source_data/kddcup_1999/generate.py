# source : https://kdd.ics.uci.edu/databases/kddcup99/task.html

import pandas as pd

classes = "back,buffer_overflow,ftp_write,guess_passwd,imap,ipsweep,land,loadmodule,multihop,neptune,nmap,normal,perl,phf,pod,portsweep,rootkit,satan,smurf,spy,teardrop,warezclient,warezmaster".split(",")
print(classes)

names = "duration protocol_type service flag src_bytes dst_bytes land wrong_fragment urgent hot num_failed_logins logged_in num_compromised root_shell su_attempted num_root num_file_creations num_shells num_access_files num_outbound_cmds is_host_login is_guest_login count srv_count serror_rate srv_serror_rate rerror_rate srv_rerror_rate same_srv_rate diff_srv_rate srv_diff_host_rate dst_host_count dst_host_srv_count dst_host_same_srv_rate dst_host_diff_srv_rate dst_host_same_src_port_rate dst_host_srv_diff_host_rate dst_host_serror_rate dst_host_srv_serror_rate dst_host_rerror_rate dst_host_srv_rerror_rate".split(" ")
print(names)

# df = pd.read_csv("kddcup.data")
column_names = names + ["intrusion_category"]

i = 0;
df = pd.DataFrame()
for chunk in pd.read_csv("kddcup.data", dtype="category", names=column_names, chunksize=100000):
    print("kddcup1999", df.shape)
    if(df.shape[0] <= 1000000):
        df = pd.concat([df, chunk], ignore_index=True)
    else:
        df.to_csv("kddcup_1999_normalized_part_" + str(i) + ".csv", index=False)
        df = pd.DataFrame()
        i = i + 1


if(df.shape[0] > 0):
    df.to_csv("kddcup_1999_normalized_part_" + str(i) + ".csv", index=False)
