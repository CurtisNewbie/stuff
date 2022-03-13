import java.util.*;
import java.time.*;
import java.math.*;

/** Some nice books */
public class Book {

    /** primary key */
    private Long id;

    /** name of the book */
    private String name;

    /** when the record is created */
    private LocalDateTime createTime;

    /** who created this record */
    private String createBy;

    /** when the record is updated */
    private LocalDateTime updateTime;

    /** who updated this record */
    private String updateBy;

    /** 0-normal, 1-deleted */
    private Integer isDel;

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public LocalDateTime getCreateTime() {
        return this.createTime;
    }

    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }

    public String getCreateBy() {
        return this.createBy;
    }

    public void setCreateBy(String createBy) {
        this.createBy = createBy;
    }

    public LocalDateTime getUpdateTime() {
        return this.updateTime;
    }

    public void setUpdateTime(LocalDateTime updateTime) {
        this.updateTime = updateTime;
    }

    public String getUpdateBy() {
        return this.updateBy;
    }

    public void setUpdateBy(String updateBy) {
        this.updateBy = updateBy;
    }

    public Integer getIsDel() {
        return this.isDel;
    }

    public void setIsDel(Integer isDel) {
        this.isDel = isDel;
    }

}
