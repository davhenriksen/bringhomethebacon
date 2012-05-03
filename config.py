#!/usr/bin/env python
# CONFIG FILE

C_rule_sources = []
C_files = []
C_db_name = 'DB.db'

########## DO NOT MODIFY VARIABLES ABOVE THIS LINE  ##########


# Specify path to tmp. dir. (must be manually created). Must be full path and path must end with a trailing slash.
# Example: '/home/user/bringhomethebacon/tmp/' 
C_tmp_dir = ''

# Specify path to ditribute dir - dir that contains all files to be ditributed (must be manually created). Must be full path and path must end with a trailing slash.
# Example: '/home/user/bringhomethebacon/files_to distribute/'
C_distribute_dir = ''

# The db must be located in the root of bringhomethebacon directory. Must be full path and path must end with a trailing slash.
# Example: '/home/user/bringhomethebacon/'
C_db_path = ''+C_db_name

# Specify path to local rules dir. Must be full path and path must end with a trailing slash.
# Example: '/home/user/rules/'
# Leave blank if not using local rules or choosing to use web-GUI to add rules.
C_locale_rule_path = ''

# Specify path and name for update.py logfile. Must be full path.
# Example: '/home/user/bringhomethebacon/updatelog.txt'
C_updatelog = ''

# Specify path and name for distribute.py logfile. Must be full path.
# Example: '/home/user/bringhomethebacon/distributelog.txt'
C_distrblog = ''


# NB: Remember to set correct permissions on folders and files!


# Select files to be moved to the distribute dir. If file already exists in that dir, it will be updated if any changes.
# The file-folder option must be specified in external sources for this to work. Use default values if not sure. 
C_files.append(['reference.config'])
C_files.append(['sid-msg.map'])
C_files.append(['gen-msg.map'])
C_files.append(['classification.config'])
C_files.append(['unicode.map'])


######################################## ADD EXTERNAL RULE SOURCES BELOW ################################################
# INFO:
# 
# Use this syntax to add more rule sources: rule_sources.append([ rule-source-name, md5-url*, rule-url**, rule-folder***, file-folder****])
# 
# * Rule-url must point to a tar.gz file
# ** Md5-url is optional. if no md5-url, keep it blank (''), else md5-url must point to a file that only contains md5 sum
# *** Rule-folder is the path (within the tar.gz) to where the rule files reside. If no folder, keep it blank: ''
# **** File-folder is the path (within the tar.gz) to where gen-msg.map, reference.config etc. reside.
# If no folder, keep it blank: ''. Else if the tar.gz dont have these files, use none: 'none'. 
#
# See VRT and ET example below for more information.
##########################################################################################################################

## VRT-rules

# Specify snort version. Example: '2920'.  Use snort -V to get snort version
C_vrt_snort_version = ''

C_oinkcode = ''

C_rule_sources.append([
        'Sourcefire',
        'http://www.snort.org/reg-rules/snortrules-snapshot-'+C_vrt_snort_version+'.tar.gz.md5/'+C_oinkcode,
        'http://www.snort.org/reg-rules/snortrules-snapshot-'+C_vrt_snort_version+'.tar.gz/'+C_oinkcode,
        'rules/',
	'etc/'
        ])

## ET-rules

# Specify snort version. Example: '2.9.0'.  Use snort -V to get snort version
C_et_snort_version = ''

C_rule_sources.append([
        'Emerging Threats',
        'http://rules.emergingthreats.net/open-nogpl/snort-'+C_et_snort_version+'/emerging.rules.tar.gz.md5',
        'http://rules.emergingthreats.net/open-nogpl/snort-'+C_et_snort_version+'/emerging.rules.tar.gz',
        'rules/',
	'rules/',
        ])
