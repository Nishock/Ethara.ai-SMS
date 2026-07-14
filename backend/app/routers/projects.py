from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Project).filter(models.Project.name == project.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project name already exists")
        
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[schemas.ProjectResponse])
def read_projects(name: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Project)
    if name:
        query = query.filter(models.Project.name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    update_data = project.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_project.name:
        existing = db.query(models.Project).filter(models.Project.name == update_data["name"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Project name already exists")

    for key, value in update_data.items():
        setattr(db_project, key, value)
        
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db.delete(db_project)
    db.commit()
    return None

@router.get("/{project_id}/employees", response_model=List[schemas.EmployeeResponse])
def get_project_employees(project_id: int, db: Session = Depends(get_db)):
    """
    List all employees mapped to a specific project.
    """
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.query(models.Employee).filter(models.Employee.project_id == project_id).all()

