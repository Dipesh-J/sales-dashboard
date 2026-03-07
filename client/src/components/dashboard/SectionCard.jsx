import './SectionCard.css';

const SectionCard = ({ title, color, children }) => {
    return (
        <div className="section-card">
            <div className="section-card-header" style={{ backgroundColor: color }}>
                {title}
            </div>
            <div className="section-card-body">
                {children}
            </div>
        </div>
    );
};

export default SectionCard;
