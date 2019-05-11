#!/bin/bash

# Uncomment to enable debug mode
#set -x
#trap read debug

# Modified from by https://wiki.postgresql.org/wiki/Automated_Backup_on_Linux

echo "$(date): execute django backups" >> /var/log/cron.log 2>&1

###########################
####### LOAD CONFIG #######
###########################
 
while [ $# -gt 0 ]; do
        case $1 in
                -c)
                        CONFIG_FILE_PATH="$2"
                        shift 2
                        ;;
                *)
                        ${ECHO} "Unknown Option \"$1\"" 1>&2
                        exit 2
                        ;;
        esac
done

if [ -n $CONFIG_FILE_PATH ] ; then
        echo "Got CONFIG_FILE_PATH from arguments : $CONFIG_FILE_PATH "
else
        echo "Could not get CONFIG_FILE_PATH from arguments. Trying from current script directory..."
fi

if [ -z $CONFIG_FILE_PATH ] ; then
        SCRIPTPATH=$(cd ${0%/*} && pwd -P)
        echo "Trying to find config file in current directory: ${SCRIPTPATH}/dj_backup.config"
        CONFIG_FILE_PATH="${SCRIPTPATH}/dj_backup.config"
fi
 
if [ ! -r ${CONFIG_FILE_PATH} ] ; then
        echo "Could not load config file from ${CONFIG_FILE_PATH}" 1>&2
        exit 1
else
        echo "Config file sucessfully loaded"
fi
 
source "${CONFIG_FILE_PATH}"
 
 
###########################
#### START THE BACKUPS ####
###########################
echo "declaring function perform_backups()"

function perform_backups()
{
	SUFFIX=$1
	FINAL_BACKUP_DIR=$BACKUP_DIR"`date +\%Y-\%m-\%d`$SUFFIX/"
 
	echo "Making backup directory in $FINAL_BACKUP_DIR"
 
	if ! mkdir -p $FINAL_BACKUP_DIR; then
		echo "Cannot create backup directory in $FINAL_BACKUP_DIR. Go and fix it!" 1>&2
		exit 1;
	fi;
 
	#######################
	### GLOBALS BACKUPS ###
	#######################
 
	echo -e "\n\nPerforming globals backup"
	echo -e "--------------------------------------------\n"
 
	if [ $ENABLE_GLOBALS_BACKUPS = "yes" ]
	then
		    echo "Globals backup"
 
		    if ! /srv/$DJANGO_PROJECT_NAME/manage.py dumpdata | gzip > $FINAL_BACKUP_DIR"globals".json.gz.in_progress; then
		            echo "[!!ERROR!!] Failed to produce globals backup" 1>&2
		    else
		            mv $FINAL_BACKUP_DIR"globals".json.gz.in_progress $FINAL_BACKUP_DIR"globals".json.gz
		    fi
	else
		echo "None"
	fi
 
 
	###########################
	###### SAFE BACKUPS #######
	###########################
 
 	echo -e "\n\nPerforming safe backup"
	echo -e "--------------------------------------------\n"
 
	if [ $ENABLE_SAFE_BACKUPS = "yes" ]
	then
		    echo "Safe backup"
 
		    if ! /srv/$DJANGO_PROJECT_NAME/manage.py dumpdata --exclude auth.permission --exclude contenttypes | gzip > $FINAL_BACKUP_DIR"safe".json.gz.in_progress; then
		            echo "[!!ERROR!!] Failed to produce safe backup" 1>&2
		    else
		            mv $FINAL_BACKUP_DIR"safe".json.gz.in_progress $FINAL_BACKUP_DIR"safe".json.gz
		    fi
	else
		echo "None"
	fi
  
	echo -e "\nAll database backups complete!"
}

echo "Starting backups..."

# MONTHLY BACKUPS
 
DAY_OF_MONTH=`date +%d`
 
if [ $DAY_OF_MONTH -eq 1 ];
then
	# Delete all expired monthly directories
	find $BACKUP_DIR -maxdepth 1 -name "*-monthly" -exec rm -rf '{}' ';'
 
	perform_backups "-monthly"
  echo "Mounthly backups performed. Exiting..."
	exit 0;
else
    echo "No mountly backup planned today"
fi
 
# WEEKLY BACKUPS
 
DAY_OF_WEEK=`date +%u` #1-7 (Monday-Sunday)
EXPIRED_DAYS=`expr $((($WEEKS_TO_KEEP * 7) + 1))`
 
if [ $DAY_OF_WEEK = $DAY_OF_WEEK_TO_KEEP ];
then
	  # Delete all expired weekly directories
	  find $BACKUP_DIR -maxdepth 1 -mtime +$EXPIRED_DAYS -name "*-weekly" -exec rm -rf '{}' ';'
 
	  perform_backups "-weekly"
    echo "Weekly backups performed. Exiting..."
	  exit 0;
else
    echo "No weekly backup planned today"
fi
 
# DAILY BACKUPS

echo "ENABLE_DAILY_BACKUPS is settled to $ENABLE_DAILY_BACKUPS "

if [ $ENABLE_DAILY_BACKUPS = "yes" ];
then 
    # Delete daily backups 7 days old or more
    find $BACKUP_DIR -maxdepth 1 -mtime +$DAYS_TO_KEEP -name "*-daily" -exec rm -rf '{}' ';'
    
    perform_backups "-daily"
    echo "Weekly backups performed. Exiting..."
    exit 0;
else
    echo "Daily backups desactivated in config file. Set ENABLE_DAILY_BACKUPS=yes if needed;" 
fi

echo "End of file. Exiting..."

# EOF