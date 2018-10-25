## Redmine

采用docker-compose顺利搭建了redmine，但是在使用时发现无法插入中文字符，始终报internal server error错误，后来看日志，显示插入异常，现在终于明白为啥很多人安装不适用官方镜像了，问题出现了，总得解决吧，进一步分析原因是由于数据库的字符集是latin1，终于明白问题所在，然后去看了下官方给的脚本，默认是使用的utf8编码，所有的数据库表创建都是未指定字符集的，因此采用数据库脚本来变更，要想把所有的数据表的字符集改变为utf-8，手动的方式是不可取的，可能误操作数据库，因此采用存储过程来实现，下面给出存储过程脚本。

```sql
DELIMITER $$
 
CREATE PROCEDURE `redmine`.`update_char_set`()
 
    BEGIN
     DECLARE done INT DEFAULT 0;
     DECLARE t_sql VARCHAR(256);
     DECLARE tableName VARCHAR(128);
     DECLARE lists CURSOR FOR SELECT table_name FROM `information_schema`.`TABLES` WHERE table_schema = 'redmine';
     DECLARE CONTINUE HANDLER FOR SQLSTATE '02000' SET done = 1;
     OPEN lists;
     FETCH lists INTO tableName;
     REPEAT
        SET @t_sql = CONCAT('ALTER TABLE ', tableName, ' CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci');
        PREPARE stmt FROM @t_sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
     FETCH lists INTO tableName;
     UNTIL done END REPEAT;
     CLOSE lists;
    END$$
 
DELIMITER ;
```

将存储过程在数据库所在的服务器上执行一遍，

然后是改变数据库的字符集和字符集合，再更新每个数据表的，执行脚本如下：

```sql
use redmine;
ALTER DATABASE redmine DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
CALL redmine.update_char_set();
```

最后再通过创建项目，插入中文字符成功，问题完美解决。